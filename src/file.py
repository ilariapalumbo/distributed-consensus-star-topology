class File:
    def __init__(self, file_name, content, version=1):
        """
        Represents a file with a name, content, size, and version
	params:
        file_name: The name of the file, including its extension
        content: The content of the file
        version: The version of the file
        """
        self.file_name = file_name
        self.content = content
        self.size = len(content.encode("utf-8"))  # File size in bytes
        self.version = version

    def is_valid(self, max_size=100_000):
        """
        Validates the file
	params:
        max_size: Maximum allowed file size in bytes
        Return a tuple (bool, message). True if the file is valid, otherwise False with an explanation
        """
        if not self.file_name.endswith(".txt"):
            return False, "File must have a .txt extension."
        if self.size > max_size:
            return False, f"File size exceeds the limit of {max_size} bytes (actual: {self.size} bytes)."
        return True, "File is valid."
