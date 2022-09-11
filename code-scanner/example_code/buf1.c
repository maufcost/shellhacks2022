#include <stdio.h>
#include <stdlib.h>


void getName(){
	printf("What's your name? ");

	char name[15] = {0};
	fgets(name, 100, stdin);

	printf("Cool name %s!", name);

}


int main(){
	getName();
}

void openShell(){
	system("/bin/sh");
}
