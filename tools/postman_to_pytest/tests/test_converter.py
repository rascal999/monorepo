"""Test the Postman to pytest converter."""

import logging
import re
from pathlib import Path

import pytest

from postman2pytest.parser import parse_collection
from postman2pytest.generator import create_test_generator
from postman2pytest.auth import AuthHandler

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)


def test_parse_collection(tmp_path):
    """Test parsing a Postman collection."""
    collection_path = Path(__file__).parent.parent / "collections" / "sample_api.json"
    assert collection_path.exists(), f"Collection file not found at {collection_path}"
    
    collection = parse_collection(collection_path)
    assert collection.info["name"] == "Sample API Collection"
    assert len(collection.item) == 2
    assert collection.auth["type"] == "bearer"


def test_auth_extraction(tmp_path):
    """Test extracting authentication configuration."""
    collection_path = Path(__file__).parent.parent / "collections" / "sample_api.json"
    assert collection_path.exists(), f"Collection file not found at {collection_path}"
    
    collection = parse_collection(collection_path)
    
    auth_config = AuthHandler.extract_auth_config(collection.auth)
    assert auth_config is not None
    assert auth_config.type == "bearer"
    assert auth_config.token == "sample_token_123"


def test_test_generation(tmp_path):
    """Test generating pytest files."""
    logger.info("Starting test generation test")
    
    # Use absolute path for collection file
    collection_path = Path(__file__).parent.parent / "collections" / "sample_api.json"
    logger.debug(f"Collection path: {collection_path}")
    assert collection_path.exists(), f"Collection file not found at {collection_path}"
    
    logger.debug("Parsing collection")
    collection = parse_collection(collection_path)
    logger.debug(f"Collection items: {[item.name for item in collection.item]}")
    
    logger.debug(f"Creating test generator with output dir: {tmp_path}")
    generator = create_test_generator(tmp_path)
    
    logger.debug("Generating tests")
    try:
        success = generator.generate_tests(collection)
        logger.debug(f"Test generation result: {success}")
        logger.debug(f"Output directory contents: {list(tmp_path.glob('*'))}")
    except Exception as e:
        logger.error(f"Error during test generation: {str(e)}")
        raise
    
    assert success is True, "Test generation failed"
    
    # Check generated files
    logger.debug("Checking generated files")
    test_files = list(tmp_path.glob("test_*.py"))
    logger.debug(f"Found test files: {[str(f) for f in test_files]}")
    assert len(test_files) == 2, f"Expected 2 test files, found {len(test_files)}"
    
    # List all files in tmp_path for debugging
    logger.debug("All files in output directory:")
    for file in tmp_path.rglob("*"):
        logger.debug(f"  {file}")
    
    # Verify content of generated files
    get_test = tmp_path / "test_get_get_users.py"
    logger.debug(f"Checking get test file: {get_test}")
    assert get_test.exists(), f"Get test file not found at {get_test}"
    content = get_test.read_text()
    logger.debug(f"Get test content:\n{content}")
    assert "def test_get_get_users(session):" in content, "Get test function not found"
    
    # Use regex to check for the request line, ignoring whitespace and line breaks
    get_request_pattern = re.compile(r'response\s*=\s*session\.get\s*\(\s*"https://api\.example\.com/v1/users"')
    assert get_request_pattern.search(content), "Get request not found"
    
    post_test = tmp_path / "test_post_create_user.py"
    logger.debug(f"Checking post test file: {post_test}")
    assert post_test.exists(), f"Post test file not found at {post_test}"
    content = post_test.read_text()
    logger.debug(f"Post test content:\n{content}")
    assert "def test_post_create_user(session):" in content, "Post test function not found"
    
    # Use regex to check for the request line, ignoring whitespace and line breaks
    post_request_pattern = re.compile(r'response\s*=\s*session\.post\s*\(\s*"https://api\.example\.com/v1/users"')
    assert post_request_pattern.search(content), "Post request not found"
    
    logger.info("Test generation test completed successfully")
