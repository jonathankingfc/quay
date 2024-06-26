"""
Remove 'oci' tables not used by CNR. The rest will be migrated and renamed.

Revision ID: 5cbbfc95bac7
Revises: 1783530bee68
Create Date: 2018-05-23 17:28:40.114433
"""

# revision identifiers, used by Alembic.
revision = "5cbbfc95bac7"
down_revision = "1783530bee68"

import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from util.migrate import UTF8CharField, UTF8LongText


def upgrade(op, tables, tester):
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("derivedimage")
    op.drop_table("manifestlabel")
    op.drop_table("blobplacementlocationpreference")
    op.drop_table("blobuploading")
    op.drop_table("bittorrentpieces")
    op.drop_table("manifestlayerdockerv1")
    op.drop_table("manifestlayerscan")
    op.drop_table("manifestlayer")
    # ### end Alembic commands ###


def downgrade(op, tables, tester):
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "manifestlayer",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("blob_id", sa.Integer(), nullable=False),
        sa.Column("manifest_id", sa.Integer(), nullable=False),
        sa.Column("manifest_index", sa.BigInteger(), nullable=False),
        sa.Column("metadata_json", UTF8LongText, nullable=False),
        sa.ForeignKeyConstraint(
            ["blob_id"], ["blob.id"], name=op.f("fk_manifestlayer_blob_id_blob")
        ),
        sa.ForeignKeyConstraint(
            ["manifest_id"], ["manifest.id"], name=op.f("fk_manifestlayer_manifest_id_manifest")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_manifestlayer")),
    )
    op.create_index(
        "manifestlayer_manifest_index", "manifestlayer", ["manifest_index"], unique=False
    )
    op.create_index(
        "manifestlayer_manifest_id_manifest_index",
        "manifestlayer",
        ["manifest_id", "manifest_index"],
        unique=True,
    )
    op.create_index("manifestlayer_manifest_id", "manifestlayer", ["manifest_id"], unique=False)
    op.create_index("manifestlayer_blob_id", "manifestlayer", ["blob_id"], unique=False)

    op.create_table(
        "manifestlayerscan",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("layer_id", sa.Integer(), nullable=False),
        sa.Column("scannable", sa.Boolean(), nullable=False),
        sa.Column("scanned_by", UTF8CharField(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["layer_id"],
            ["manifestlayer.id"],
            name=op.f("fk_manifestlayerscan_layer_id_manifestlayer"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_manifestlayerscan")),
    )

    op.create_index("manifestlayerscan_layer_id", "manifestlayerscan", ["layer_id"], unique=True)

    op.create_table(
        "bittorrentpieces",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("blob_id", sa.Integer(), nullable=False),
        sa.Column("pieces", UTF8LongText, nullable=False),
        sa.Column("piece_length", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["blob_id"], ["blob.id"], name=op.f("fk_bittorrentpieces_blob_id_blob")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bittorrentpieces")),
    )

    op.create_index(
        "bittorrentpieces_blob_id_piece_length",
        "bittorrentpieces",
        ["blob_id", "piece_length"],
        unique=True,
    )
    op.create_index("bittorrentpieces_blob_id", "bittorrentpieces", ["blob_id"], unique=False)

    op.create_table(
        "blobuploading",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=255), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("repository_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("byte_count", sa.BigInteger(), nullable=False),
        sa.Column("uncompressed_byte_count", sa.BigInteger(), nullable=True),
        sa.Column("chunk_count", sa.BigInteger(), nullable=False),
        sa.Column("storage_metadata", UTF8LongText, nullable=True),
        sa.Column("sha_state", UTF8LongText, nullable=True),
        sa.Column("piece_sha_state", UTF8LongText, nullable=True),
        sa.Column("piece_hashes", UTF8LongText, nullable=True),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["blobplacementlocation.id"],
            name=op.f("fk_blobuploading_location_id_blobplacementlocation"),
        ),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repository.id"],
            name=op.f("fk_blobuploading_repository_id_repository"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_blobuploading")),
    )

    op.create_index("blobuploading_uuid", "blobuploading", ["uuid"], unique=True)
    op.create_index(
        "blobuploading_repository_id_uuid", "blobuploading", ["repository_id", "uuid"], unique=True
    )
    op.create_index("blobuploading_repository_id", "blobuploading", ["repository_id"], unique=False)
    op.create_index("blobuploading_location_id", "blobuploading", ["location_id"], unique=False)
    op.create_index("blobuploading_created", "blobuploading", ["created"], unique=False)

    op.create_table(
        "manifestlayerdockerv1",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("manifest_layer_id", sa.Integer(), nullable=False),
        sa.Column("image_id", UTF8CharField(length=255), nullable=False),
        sa.Column("checksum", UTF8CharField(length=255), nullable=False),
        sa.Column("compat_json", UTF8LongText, nullable=False),
        sa.ForeignKeyConstraint(
            ["manifest_layer_id"],
            ["manifestlayer.id"],
            name=op.f("fk_manifestlayerdockerv1_manifest_layer_id_manifestlayer"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_manifestlayerdockerv1")),
    )

    op.create_index(
        "manifestlayerdockerv1_manifest_layer_id",
        "manifestlayerdockerv1",
        ["manifest_layer_id"],
        unique=False,
    )
    op.create_index(
        "manifestlayerdockerv1_image_id", "manifestlayerdockerv1", ["image_id"], unique=False
    )

    op.create_table(
        "manifestlabel",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("repository_id", sa.Integer(), nullable=False),
        sa.Column("annotated_id", sa.Integer(), nullable=False),
        sa.Column("label_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["annotated_id"], ["manifest.id"], name=op.f("fk_manifestlabel_annotated_id_manifest")
        ),
        sa.ForeignKeyConstraint(
            ["label_id"], ["label.id"], name=op.f("fk_manifestlabel_label_id_label")
        ),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repository.id"],
            name=op.f("fk_manifestlabel_repository_id_repository"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_manifestlabel")),
    )

    op.create_index(
        "manifestlabel_repository_id_annotated_id_label_id",
        "manifestlabel",
        ["repository_id", "annotated_id", "label_id"],
        unique=True,
    )
    op.create_index("manifestlabel_repository_id", "manifestlabel", ["repository_id"], unique=False)
    op.create_index("manifestlabel_label_id", "manifestlabel", ["label_id"], unique=False)
    op.create_index("manifestlabel_annotated_id", "manifestlabel", ["annotated_id"], unique=False)

    op.create_table(
        "blobplacementlocationpreference",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["blobplacementlocation.id"],
            name=op.f("fk_blobplacementlocpref_locid_blobplacementlocation"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], name=op.f("fk_blobplacementlocationpreference_user_id_user")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_blobplacementlocationpreference")),
    )
    op.create_index(
        "blobplacementlocationpreference_user_id",
        "blobplacementlocationpreference",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "blobplacementlocationpreference_location_id",
        "blobplacementlocationpreference",
        ["location_id"],
        unique=False,
    )

    op.create_table(
        "derivedimage",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=255), nullable=False),
        sa.Column("source_manifest_id", sa.Integer(), nullable=False),
        sa.Column("derived_manifest_json", UTF8LongText, nullable=False),
        sa.Column("media_type_id", sa.Integer(), nullable=False),
        sa.Column("blob_id", sa.Integer(), nullable=False),
        sa.Column("uniqueness_hash", sa.String(length=255), nullable=False),
        sa.Column("signature_blob_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["blob_id"], ["blob.id"], name=op.f("fk_derivedimage_blob_id_blob")
        ),
        sa.ForeignKeyConstraint(
            ["media_type_id"],
            ["mediatype.id"],
            name=op.f("fk_derivedimage_media_type_id_mediatype"),
        ),
        sa.ForeignKeyConstraint(
            ["signature_blob_id"], ["blob.id"], name=op.f("fk_derivedimage_signature_blob_id_blob")
        ),
        sa.ForeignKeyConstraint(
            ["source_manifest_id"],
            ["manifest.id"],
            name=op.f("fk_derivedimage_source_manifest_id_manifest"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_derivedimage")),
    )
    op.create_index("derivedimage_uuid", "derivedimage", ["uuid"], unique=True)
    op.create_index(
        "derivedimage_uniqueness_hash", "derivedimage", ["uniqueness_hash"], unique=True
    )
    op.create_index(
        "derivedimage_source_manifest_id_media_type_id_uniqueness_hash",
        "derivedimage",
        ["source_manifest_id", "media_type_id", "uniqueness_hash"],
        unique=True,
    )
    op.create_index(
        "derivedimage_source_manifest_id_blob_id",
        "derivedimage",
        ["source_manifest_id", "blob_id"],
        unique=True,
    )
    op.create_index(
        "derivedimage_source_manifest_id", "derivedimage", ["source_manifest_id"], unique=False
    )
    op.create_index(
        "derivedimage_signature_blob_id", "derivedimage", ["signature_blob_id"], unique=False
    )
    op.create_index("derivedimage_media_type_id", "derivedimage", ["media_type_id"], unique=False)
    op.create_index("derivedimage_blob_id", "derivedimage", ["blob_id"], unique=False)
    # ### end Alembic commands ###
