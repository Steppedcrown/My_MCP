from ._base import make_router

bosses_router = make_router("bosses", search_field="title", table="boss")
locations_router = make_router("locations", search_field="title", table="location")
npcs_router = make_router("npcs", search_field="title", table="npc")
dungeons_router = make_router("dungeons", search_field="title", table="dungeon")
remembrances_router = make_router("remembrances", search_field="title", table="remembrance")
weapon_classes_router = make_router("weapon-classes", search_field="class_name", table="weapon_class", tag="Weapon Classes")
weapons_router = make_router("weapons", search_field="title", table="weapon")
spells_router = make_router("spells", search_field="title", table="spell")
skills_router = make_router("skills", search_field="title", table="skill")
reusable_items_router = make_router("reusable-items", search_field="title", table="reusable_item", tag="Reusable Items")
summons_router = make_router("summons", search_field="title", table="summon")

all_routers = [
    bosses_router,
    locations_router,
    npcs_router,
    dungeons_router,
    remembrances_router,
    weapon_classes_router,
    weapons_router,
    spells_router,
    skills_router,
    reusable_items_router,
    summons_router,
]
