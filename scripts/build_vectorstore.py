#!/usr/bin/env python3
# =============================================================
# scripts/build_vectorstore.py
# Build the FAISS RAG index for Money Matters.
#
# Run this ONCE after cloning the repo, and again whenever
# you want to refresh the knowledge base.
#
# Usage:
#   python scripts/build_vectorstore.py
#   python scripts/build_vectorstore.py --dynamic-only
#   python scripts/build_vectorstore.py --upload-cos
# =============================================================

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.pipeline import ingest_and_index
from utils.logger import logger


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the Money Matters FAISS RAG vector store."
    )
    parser.add_argument(
        "--dynamic-only",
        action="store_true",
        help="Only ingest dynamic (RSS) sources. Skip static web pages.",
    )
    parser.add_argument(
        "--upload-cos",
        action="store_true",
        help="After building, upload the index to IBM Cloud Object Storage.",
    )
    parser.add_argument(
        "--no-local",
        action="store_true",
        help="Skip local PDF documents.",
    )
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Money Matters — Build Vector Store")
    logger.info("=" * 60)

    summary = ingest_and_index(
        include_static  = not args.dynamic_only,
        include_dynamic = True,
        include_local   = not args.no_local,
    )

    if summary["status"] == "success":
        logger.info("✅ Success!")
        logger.info("   Documents : {}", summary["documents"])
        logger.info("   Chunks    : {}", summary["chunks"])
        logger.info("   Vectors   : {}", summary["vectors"])
        logger.info("   Dimension : {}", summary["dim"])

        if args.upload_cos:
            logger.info("Uploading index to IBM COS...")
            try:
                from data.embeddings import faiss_path, meta_path
                from services.cos_service import upload_rag_index
                from pathlib import Path as P
                _base = P(__file__).resolve().parent.parent / "data" / "embeddings"
                ok = upload_rag_index(_base / "faiss.index", _base / "metadata.json")
                if ok:
                    logger.info("✅ Index uploaded to IBM COS.")
                else:
                    logger.warning("COS upload failed — check credentials.")
            except Exception as exc:
                logger.error("COS upload error: {}", exc)
    else:
        logger.error("❌ Build failed: {}", summary.get("message"))
        sys.exit(1)


if __name__ == "__main__":
    main()
