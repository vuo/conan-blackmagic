#include <DeckLinkAPI.h>

int main()
{
	// Create an IDeckLinkIterator object to enumerate all DeckLink cards in the system
	// It will return NULL since the DeckLink drivers aren't installed,
	// but that's OK since we just want to ensure it builds and runs without crashing.
	CreateDeckLinkIteratorInstance();
	return 0;
}
