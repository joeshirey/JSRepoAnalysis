import unittest
import os
from tools.extract_region_tags import RegionTagExtractor
from utils.exceptions import RegionTagError


class TestRegionTagExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = RegionTagExtractor()
        self.test_file_with_tags = "test_file_with_tags.txt"
        with open(self.test_file_with_tags, "w") as f:
            f.write("// [START tag1]\n")
            f.write("some code\n")
            f.write("// [END tag1]\n")
            f.write("# [START tag2]\n")
            f.write("some other code\n")
            f.write("# [END tag2]\n")
            f.write("// [START tag1] \n")  # with extra space
            f.write("// [START tag3] \n")

        self.test_file_without_tags = "test_file_without_tags.txt"
        with open(self.test_file_without_tags, "w") as f:
            f.write("some code without tags\n")

    def tearDown(self):
        if os.path.exists(self.test_file_with_tags):
            os.remove(self.test_file_with_tags)
        if os.path.exists(self.test_file_without_tags):
            os.remove(self.test_file_without_tags)

    def test_extract_from_file_with_tags(self):
        expected_tags = sorted(["tag1", "tag2", "tag3"])
        self.assertEqual(
            self.extractor.execute(self.test_file_with_tags), expected_tags
        )

    def test_extract_from_file_without_tags(self):
        self.assertEqual(self.extractor.execute(self.test_file_without_tags), [])

    def test_extract_from_nonexistent_file(self):
        with self.assertRaises(RegionTagError):
            self.extractor.execute("nonexistent_file.txt")

    def test_extract_from_empty_file(self):
        empty_file = "empty_file.txt"
        open(empty_file, "a").close()
        self.assertEqual(self.extractor.execute(empty_file), [])
        os.remove(empty_file)


if __name__ == "__main__":
    unittest.main()
