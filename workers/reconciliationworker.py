import datetime
import logging
import time

import features
from app import app
from app import billing as stripe
from app import marketplace_subscriptions, marketplace_users
from data import model
from data.billing import RECONCILER_SKUS, get_plan
from data.model import entitlements
from util.locking import GlobalLock, LockNotAcquiredException
from workers.gunicorn_worker import GunicornWorker
from workers.namespacegcworker import LOCK_TIMEOUT_PADDING
from workers.worker import Worker

logger = logging.getLogger(__name__)

RECONCILIATION_TIMEOUT = 5 * 60  # 5min
LOCK_TIMEOUT_PADDING = 60  # 60
RECONCILIATION_FREQUENCY = 5 * 60  # run reconciliation every 5 min

MILLISECONDS_IN_SECONDS = 1000
SECONDS_IN_DAYS = 86400
ONE_MONTH = 30 * SECONDS_IN_DAYS * MILLISECONDS_IN_SECONDS


class ReconciliationWorker(Worker):
    def __init__(self):
        super(ReconciliationWorker, self).__init__()
        self.add_operation(
            self._reconcile_entitlements,
            app.config.get("RECONCILIATION_FREQUENCY", RECONCILIATION_FREQUENCY),
        )

    def _perform_reconciliation(self, user_api, marketplace_api):
        """
        Gather all entitlements from internal marketplace api and store in quay db
        Create new entitlements for stripe customers if needed
        """
        logger.info("Reconciliation worker looking to create new subscriptions...")

        users = model.user.get_active_users()

        stripe_users = [user for user in users if user.stripe_id is not None]

        for user in stripe_users:

            email = user.email
            model_customer_id = entitlements.get_web_customer_id(user.id)
            logger.debug(
                "Database returned %s customer id for %s", str(model_customer_id), user.username
            )

            # check against user api
            customer_id = user_api.lookup_customer_id(email)
            logger.debug("Found %s number for %s", str(customer_id), email)

            if model_customer_id is None and customer_id:
                logger.debug("Saving new customer id %s for %s", customer_id, user.username)
                entitlements.save_web_customer_id(user, customer_id)
            elif model_customer_id != customer_id:
                # what is in the database differs from the service
                # take the service and store in the database instead
                if customer_id:
                    logger.debug(
                        "Reconciled differing ids for %s, changing from %s to %s",
                        user.username,
                        model_customer_id,
                        customer_id,
                    )
                    entitlements.update_web_customer_id(user, customer_id)
                else:
                    # user does not have a web customer id from api and should be removed from table
                    logger.debug(
                        "Removing conflicting id %s for %s", model_customer_id, user.username
                    )
                    entitlements.remove_web_customer_id(user, model_customer_id)
            elif customer_id is None:
                logger.debug("User %s does not have an account number", user.username)
                continue

            # check if we need to create a subscription for customer in RH marketplace
            try:
                stripe_customer = stripe.Customer.retrieve(user.stripe_id)
            except stripe.error.APIConnectionError:
                logger.error("Cannot connect to Stripe")
                continue
            except stripe.error.InvalidRequestError:
                logger.warn("Invalid request for stripe_id %s", user.stripe_id)
                continue
            for sku_id in RECONCILER_SKUS:
                if stripe_customer.subscription:
                    plan = get_plan(stripe_customer.subscription.plan.id)
                    if plan is None:
                        continue
                    if plan.get("rh_sku") == sku_id:
                        subscription = marketplace_api.lookup_subscription(customer_id, sku_id)
                        if subscription is None:
                            logger.debug("Found %s to create for %s", sku_id, user.username)
                            marketplace_api.create_entitlement(customer_id, sku_id)
                        break
                else:
                    logger.debug("User %s does not have a stripe subscription", user.username)

            logger.debug("Finished work for user %s", user.username)

        logger.info("Reconciliation worker is done")

    def _reconcile_entitlements(self, skip_lock_for_testing=False):
        """
        Performs reconciliation for user entitlements
        """
        # try to acquire lock
        if skip_lock_for_testing:
            self._perform_reconciliation(
                user_api=marketplace_users, marketplace_api=marketplace_subscriptions
            )
        else:
            try:
                with GlobalLock(
                    "RECONCILIATION_WORKER",
                    lock_ttl=RECONCILIATION_TIMEOUT + LOCK_TIMEOUT_PADDING,
                ):
                    self._perform_reconciliation(
                        user_api=marketplace_users, marketplace_api=marketplace_subscriptions
                    )
            except LockNotAcquiredException:
                logger.debug("Could not acquire global lock for entitlement reconciliation")
                print(str(LockNotAcquiredException))


def create_gunicorn_worker():
    """
    Follows the gunicorn application factory pattern, enabling
    a quay worker to run as a gunicorn worker thread
    """
    worker = GunicornWorker(
        __name__, app, ReconciliationWorker(), features.ENTITLEMENT_RECONCILIATION
    )
    return worker


if __name__ == "__main__":
    if not features.ENTITLEMENT_RECONCILIATION:
        logger.debug("Reconciliation worker disabled; skipping")
        while True:
            time.sleep(1000)
    GlobalLock.configure(app.config)
    logger.debug("Starting reconciliation worker")
    worker = ReconciliationWorker()
    worker.start()
