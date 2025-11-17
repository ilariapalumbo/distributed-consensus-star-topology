import time
import hashlib

class ConsensusAlgorithm:
    def __init__(self, servers):
        """
	Represents the consensus algorithm logic
	params:
        servers: a list of Server objects forming the cluster
        """
        self.servers = servers
        self.unresponsive_servers = set()
        self.unavailable_servers = set()

    def validate_file(self, file):
        """
        Validates a file before it is sent to the servers
	Return True if the file is valid, otherwise False
	params:
        file: a File object
        """
        is_valid, message = file.is_valid()
        if not is_valid:
            print(f"Consensus: Validation failed - {message} \n")
            return False
        return True

    def update_consensus(self, file, timeout_ms=2, retry_limit=3, retry_period_ms=5):
        """
        Handles the update phase with a client-side timeout for ACKs
        Retries sending updates if ACKs are not received, respecting retry limits and periods
        Simulates server failures and recovery
	Return True if consensus was reached (all servers responded with ACKs), False otherwise
	params:
        file: the file to be updated
        timeout_ms: maximum time in milliseconds to wait for ACKs
        retry_limit: Maximum number of retries for unresponsive servers
        retry_period_ms: Period in milliseconds between retries for unresponsive servers
        current_time_ms: The current simulation time in milliseconds
        """
        print(f"Consensus: Starting update for file {file.file_name}, version {file.version}\n")
        current_time_ms = int(time.time() * 1000)
        remaining_servers = set(self.servers)  # Start with all servers
        retries = {server: 0 for server in remaining_servers}

        while remaining_servers:
            for server in list(remaining_servers):
                try:
                    if retries[server] >= retry_limit:
                        print(f"Consensus: Server {server.id} has reached max retries. Marking as unresponsive.\n")
                        self.unresponsive_servers.add(server)
                        remaining_servers.remove(server)
                        continue

                    # Send the update to the server
                    update_applied = server.update_file(file, current_time_ms)
                    if not update_applied:
                        print(f"Consensus: Server {server.id} failed to apply the update.\n")
                        retries[server] += 1
                        continue
                    start_time = time.time()

                    # Wait for ACK
                    while time.time() - start_time < timeout_ms / 1000.0:
                        ack = server.send_ack()
                        if ack:
                            print(f"Consensus: ACK received from Server {server.id}.\n")
                            remaining_servers.remove(server)
                            break
                        time.sleep(0.001)
                    else:
                        print(f"Consensus: Timeout waiting for ACK from Server {server.id}. Retrying...\n")
                        retries[server] += 1
                except Exception as e:
                    print(f"Consensus: Server {server.id} encountered an error: {e}\n")
                    retries[server] += 1

            if remaining_servers:
                print(f"Consensus: Waiting {retry_period_ms} ms before next retry for remaining servers.\n")
                time.sleep(retry_period_ms / 1000)  # Convert ms to seconds for sleep

            # Log the current state of retries
            print(f"Consensus: Current retries: {[f'Server {s.id}: {retries[s]} retries' for s in remaining_servers]}\n")

            # Break if retry limits are exhausted
            if all(retries[s] >= retry_limit for s in remaining_servers):
                print("Consensus: Retry limit reached for all remaining servers.\n")
                break

        # Return True if all servers have sent ACKs (remaining_servers is empty)
        if not remaining_servers:
            print("Consensus: All servers responded with ACKs. Update successful.\n")
            return True

        # Return False if some servers are still unresponsive
        print("Consensus: Some servers did not respond with ACKs.\n")
        return False


    def retry_unresponsive_servers(self, file, long_retry_limit=5, retry_interval=0.02):
        """
        Periodically retries to update temporarily unavailable servers
	params:
        file: The file to be updated
        long_retry_limit: Maximum number of retries for unresponsive servers
        retry_interval: Time in seconds between retries
        """
        retries = 0
        while self.unresponsive_servers and retries < long_retry_limit:
            print(f"Consensus: Retry {retries + 1} for unresponsive servers: {[s.id for s in self.unresponsive_servers]}\n")
            for server in self.unresponsive_servers.copy():
                try:
                    update_applied = server.update_file(file)
                    if update_applied:
                        ack = server.send_ack()
                        if ack:
                            self.unresponsive_servers.remove(server)
                            print(f"Consensus: Server {server.id} successfully updated.\n")
                except Exception as e:
                    print(f"Consensus: Server {server.id} is still unavailable: {e}\n")

            retries += 1
            if self.unresponsive_servers:
                print(f"Consensus: Waiting {retry_interval * 1000:.2f} ms before next retry...\n")
                time.sleep(retry_interval)

        if self.unresponsive_servers:
            print(f"Consensus: Following servers are permanently unavailable: {[s.id for s in self.unresponsive_servers]}\n")
            self.unavailable_servers.update(self.unresponsive_servers)
            self.unresponsive_servers.clear()

    def restore_consensus(self, retry_limit=2, retry_period_ms=5):
        """
        Handles the restore phase with majority rule and weighted fallback
	Return the file with the highest weight or consensus result
	params:
        retry_limit: Maximum number of retries if consensus is not reached
        retry_period_ms: Time in milliseconds between retries
        """
        print("Consensus: Starting restore phase with weighted fallback.\n")

        remaining_servers = set(self.servers)
        retries = {server: 0 for server in remaining_servers}
        all_responses = []

        for attempt in range(retry_limit):
            print(f"Consensus: Attempt {attempt + 1} to retrieve files from servers.\n")
            responses = []

            for server in list(remaining_servers):
                response = server.retrieve_file()
                if response:
                    responses.append((server.weight, response)) # Include server weight
                    remaining_servers.remove(server)
                else:
                    retries[server] += 1
                    if retries[server] >= retry_limit:
                        print(f"Consensus: Server {server.id} marked as unavailable.\n")
                        self.unresponsive_servers.add(server)
                        remaining_servers.remove(server)

            all_responses.extend(responses)

            if not remaining_servers:
                break

            print(f"Consensus: Waiting {retry_period_ms} ms before retrying.\n")
            time.sleep(retry_period_ms / 1000.0)

        if not all_responses:
            print("Consensus: No files retrieved from any server.\n")
            return None

        # Group files by hash and calculate weights
        weighted_files = {}
        for weight, response in all_responses:
            file_hash = hashlib.sha256(response["content"].encode()).hexdigest()
            if file_hash not in weighted_files:
                weighted_files[file_hash] = {"total_weight": 0, "file": response}
            weighted_files[file_hash]["total_weight"] += weight

        # Apply majority rule based on hash
        majority_file = None
        total_servers = len(self.servers) - len(self.unresponsive_servers)
        for file_hash, data in weighted_files.items():
            count = sum(1 for _, response in all_responses if hashlib.sha256(response["content"].encode()).hexdigest() == file_hash)
            if count > total_servers / 2:  # Majority rule
                majority_file = data["file"]
                print(f"Consensus: Majority file selected: {majority_file['file_name']} (Hash: {file_hash}).\n")
                return {
                    "version": majority_file["version"],
                    "content": majority_file["content"],
                    "file_name": majority_file["file_name"],
                }

        # Fallback to highest weight if no majority
        most_weighted_file = max(weighted_files.values(), key=lambda x: x["total_weight"])
        print(f"Consensus: No majority. Falling back to file with highest weight: {most_weighted_file['file']['file_name']}, Total weight: {most_weighted_file['total_weight']}.\n")
        return {
            "version": most_weighted_file["file"]["version"],
            "content": most_weighted_file["file"]["content"],
            "file_name": most_weighted_file["file"]["file_name"],
        }