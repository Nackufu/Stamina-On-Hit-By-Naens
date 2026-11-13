#include <assert.h>
#include <stdio.h>
#include "../src/hit_filter.h"
int main(void) {
    unsigned cases = 0;
    for (unsigned weapon = 0; weapon < 20; ++weapon)
        for (unsigned flags = 0; flags < 16; ++flags) {
            bool expected = weapon >= 1 && weapon <= 6 && !(flags & 4);
            assert(nsh_qualifies(true, true, true, 62, 41, weapon, 0, flags) == expected);
            ++cases;
        }
    assert(!nsh_qualifies(false,true,true,62,41,1,0,0)); /* magic repeat */
    assert(!nsh_qualifies(true,false,true,62,41,1,0,0)); /* non-actor attacker */
    assert(!nsh_qualifies(true,true,false,62,41,1,0,0)); /* self */
    assert(!nsh_qualifies(true,true,true,61,41,1,0,0)); /* scenery */
    assert(!nsh_qualifies(true,true,true,62,22,1,0,0)); /* spell */
    assert(!nsh_qualifies(true,true,true,62,41,1,123,0)); /* projectile */
    printf("PASS: %u type/flag combinations and 6 exclusion cases\n", cases);
}
