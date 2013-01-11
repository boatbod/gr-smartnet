#ifndef smartnet_types_H
#define smartnet_types_H

//datatypes for smartnet decoder

struct smartnet_packet {
	unsigned int address;
	bool groupflag;
	unsigned int command;
	unsigned int crc;
};

#endif //smartnet_types_H