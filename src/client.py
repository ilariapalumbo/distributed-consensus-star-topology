from file import File


class Client:
    def __init__(self, servers, consensus):
        """
        Represents the client
	params:
        servers: A list of server objects
        consensus: The consensus algorithm object
        """
        self.servers = servers
        self.consensus = consensus
        self.current_file = None

    def create_initial_file(self, file_name, content):
        """
        Creates the initial file
	params:
        file_name: Name of the file
        content: Content of the file
        """
        self.current_file = File(file_name=file_name, content=content)
        print(f"Client: Initial file created - {self.current_file.file_name}, Version: {self.current_file.version}\n")

    def distribute_file(self):
        """
        Distributes the initial file to all servers
        """
        print("Client: Distributing the initial file to all servers.\n")
        for server in self.servers:
            server.store_file(version=self.current_file.version, file=self.current_file)

    def update_file(self):
        """
        Updates the current file by creating a new version
        The file name and content are updated based on the version
        """
        if not self.current_file:
            print("Client: No file exists to update.\n")
            return
        new_version = self.current_file.version + 1
        new_name = f"updated_file_v{new_version}.txt"
        new_content = f"Updated content for version {new_version}."
        self.current_file = File(file_name=new_name, content=new_content, version=new_version)
        print(f"Client: File updated - {self.current_file.file_name}, Version: {self.current_file.version}\n")

    def apply_update(self):
        """
        Applies the update to the servers using the consensus algorithm
        """
        print("Client: Applying update to servers via consensus.\n")
        success = self.consensus.update_consensus(self.current_file)
        if success:
            print("Client: Update successfully applied to all servers.\n")

    def restore_file(self):
        """
        Attempts to restore the correct file from the servers using the consensus algorithm
        """
        print("Client: Attempting to restore the file.\n")
        restored_file = self.consensus.restore_consensus()
        if isinstance(restored_file, dict):
            print(
                f"Client: File restored successfully - {restored_file['file_name']}, Version: {restored_file['version']}\n")
        else:
            print(f"Client: Restore failed. Multiple versions received:\n{restored_file}\n")
