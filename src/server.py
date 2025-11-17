import hashlib
import random

class Server:
    def __init__(self, id, failure_prob ,weight, recovery_delay_min, recovery_delay_max):
        """
        Represents a server node
	params:
        id: a unique identifier for the server
        """
        self.id = id
        self.file_version = None
        self.file_content = None
        self.file_hash = None
        self.file_name = None
        self.operational = True  # Indicates if the server is currently operational
        self.recovery_time_ms = 0  # Time in ms when the server will recover if not operational
        self.failure_prob = failure_prob
        self.weight = weight
        self.recovery_delay_min = recovery_delay_min
        self.recovery_delay_max = recovery_delay_max

    def store_file(self, version, file, sender="client"):
        """
        Stores a file initially sent by the client
	params:
        version: the version of the file
        file: a File object
        """
        if sender != "client":
            print(f"Server {self.id}: Store rejected - unauthorized sender.\n")
            return
        is_valid, message = file.is_valid()
        if not is_valid:
            print(f"Server {self.id}: Validation failed - {message}")
            return
        self.file_version = version
        self.file_content = file.content
        self.file_hash = hashlib.sha256(file.content.encode()).hexdigest()
        print(f"Server {self.id}: File stored. Version: {version}, Hash: {self.file_hash}.\n")

    def update_file(self, file, current_time_ms, sender="client"):
        """
        Updates the stored file with a new version, if valid and the server is operational
        If the server is not operational, it simulates a failure
	Return: True if the update was applied, False otherwise
	params:
        file: a File object to update
        current_time_ms: the current simulation time in milliseconds
        """
        if not self.operational:
            if current_time_ms >= self.recovery_time_ms:
                # Server becomes operational again
                self.operational = True
                print(f"Server {self.id}: Recovered and operational.\n")
            else:
                print(f"Server {self.id}: Not operational.\n")
                return False

        # Validate the file before applying the update
        if sender != "client":
            print(f"Server {self.id}: Update rejected - unauthorized sender.\n")
            return
        is_valid, message = file.is_valid()
        if not is_valid:
            print(f"Server {self.id}: Validation failed - {message}\n")
            return False

        # Check if the file version is newer than the current version
        if self.file_version is not None and file.version <= self.file_version:
            print(f"Server {self.id}: Update rejected - Received version {file.version} "
                  f"is not newer than current version {self.file_version}.\n")
            return False

        # Simulate a random failure in applying the update
        if random.random() < self.failure_prob:
            self.operational = False
            random_delay = random.randint(self.recovery_delay_min, self.recovery_delay_max)
            self.recovery_time_ms = current_time_ms + random_delay
            print(f"Server {self.id}: Failed to apply the update.\n")
            return False

        # Apply the update
        self.file_version = file.version
        self.file_content = file.content
        self.file_name = file.file_name
        self.file_hash = hashlib.sha256(file.content.encode()).hexdigest()
        print(f"Server {self.id}: File updated successfully. Version: {self.file_version}, Hash: {self.file_hash}.\n")
        return True

    def send_ack(self):
        """
        Sends an acknowledgment only if the update was successfully applied
        Return: a dictionary representing the ACK status
        """
        print(f"Server {self.id}: ACK sent.\n")
        return {"status": "received", "server_id": self.id}

    def retrieve_file(self):
        """
        Returns the current file content and its version
        Simulates a failure with a configurable probability
        """
        if random.random() < 0.2:  # 20% probability of failure
            print(f"Server {self.id}: Simulated failure. No file returned.\n")
            return None

        if self.file_version and self.file_content:
            print(f"Server {self.id}: Returning file. Version: {self.file_version}, Hash: {self.file_hash}.\n")
            return {
                "server_id": self.id,
                "version": self.file_version,
                "content": self.file_content,
                "file_name": self.file_name,
            }
        else:
            print(f"Server {self.id}: No valid file available.\n")
            return None



