pragma solidity ^0.5.0;

contract CareBlock {
	uint public patientCount = 0;

	struct Patient {
		uint id;
		string IPFSCareBlock; // address of patient.json file which contains references to all their data
		bool verified;
		string orgId;	// organization user is tied to
	}

	mapping(address => Patient) public patients;

	constructor () public {
		// this is just used for testing
		addPatient(
			0xAd663308B4c65C23bb01C08a002331D1d8878C71,
			'QmZtdeqehYHM6ahSsgRJdS7kMR1FMBuU9Dyup9CnSfEC3U'
		);
	}

	function addPatient(address _patientAddress, string memory _ipfsAddress) public {
		patientCount++;
		patients[_patientAddress] = Patient(patientCount, _ipfsAddress, false, '');
		// emit event if needed
	}

	function updatePatientIPFS(address _patientAddress, string memory _ipfsAddress) public {
		// Update patient's hash on IPFS
		patients[_patientAddress].IPFSCareBlock = _ipfsAddress;
	}

	function verifyPatient(address _patientAddress, bool isVerified, string memory _orgId) public {
		// Update patient verification status
		patients[_patientAddress].verified = isVerified;
		patients[_patientAddress].orgId = _orgId;
	}
}