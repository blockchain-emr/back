pragma solidity ^0.5.0;

contract CareBlock {
	uint public patientCount = 0;

	struct Patient {
		uint id;
		string name;
		string IPFSCareBlock;
		bool verified;
	}

	mapping(address => Patient) public patients;

	constructor () public {
		addPatient(
			0xAd663308B4c65C23bb01C08a002331D1d8878C71,
			"James T. Kirk",
			'QmZtdeqehYHM6ahSsgRJdS7kMR1FMBuU9Dyup9CnSfEC3U'
		);
	}

	function addPatient(address _patientAddress, string memory name, string memory _ipfsAddress) public {
		patientCount++;
		patients[_patientAddress] = Patient(patientCount, name, _ipfsAddress, false);
		// emit event if needed
	}
}