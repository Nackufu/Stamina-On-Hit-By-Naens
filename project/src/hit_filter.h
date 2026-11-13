#ifndef NSH_HIT_FILTER_H
#define NSH_HIT_FILTER_H
#include <stdint.h>
#include <stdbool.h>

/* SKSE 1.7.3: WEAP=41, ACHR=62; weapon animation types 1..6. */
static inline bool nsh_qualifies(bool physical_context, bool actor_attacker,
                                bool distinct_target, uint8_t target_type,
                                uint8_t source_type, uint8_t weapon_type,
                                uint32_t projectile, uint8_t flags) {
    return physical_context && actor_attacker && distinct_target &&
           target_type == 62 && source_type == 41 &&
           weapon_type >= 1 && weapon_type <= 6 &&
           projectile == 0 && !(flags & 4); /* exclude bash; include power/block */
}
#endif
