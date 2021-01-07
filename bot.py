import os
import discord
import requests
import json
import logging
import sys
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
from dotenv import load_dotenv

# import subprocess

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all(), chunk_guilds_at_startup=True,
                   case_insensitive=True)
load_dotenv()

token = os.getenv('token')
crabwings_role_id = int(os.getenv('crabwings_role_id'))
duckfeet_role_id = int(os.getenv('duckfeet_role_id'))
elktail_role_id = int(os.getenv('elktail_role_id'))
client_role_id = int(os.getenv('client_role_id'))
subuser_role_id = int(os.getenv('subuser_role_id'))
verified_role_id = int(os.getenv('verified_role_id'))
guild_id = int(os.getenv('guild_id'))
verification_channel = int(os.getenv('verification_channel'))
verification_message = int(os.getenv('verification_message'))
application_api_key = os.getenv('application_api_key')
cookies = {
    'pterodactyl_session': 'eyJpdiI6InhIVXp5ZE43WlMxUU1NQ1pyNWRFa1E9PSIsInZhbHVlIjoiQTNpcE9JV3FlcmZ6Ym9vS0dBTmxXMGtST2xyTFJvVEM5NWVWbVFJSnV6S1dwcTVGWHBhZzdjMHpkN0RNdDVkQiIsIm1hYyI6IjAxYTI5NDY1OWMzNDJlZWU2OTc3ZDYxYzIyMzlhZTFiYWY1ZjgwMjAwZjY3MDU4ZDYwMzhjOTRmYjMzNDliN2YifQ%3D%3D',
}

logging.basicConfig(filename='console.log',
                    level=logging.INFO,
                    format='[%(asctime)s %(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    )
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


async def analyze_timings(message):
    enterless_message = message.content.replace("\n", " ")
    words = enterless_message.split(" ")
    timings_url = ""
    for word in words:
        if word.startswith("https://timings.") and "/?id=" in word:
            timings_url = word
            break
        if word.startswith("https://www.spigotmc.org/go/timings?url=") or word.startswith("https://timings.spigotmc.org/?url="):
            embed_var = discord.Embed(title="Timings Analysis", color=0x55ffff)
            embed_var.add_field(name="❌ Spigot",
                                value="Upgrade to [Purpur](https://ci.pl3x.net/job/Purpur/).",
                                inline=True)
            await message.channel.send(embed=embed_var)
            return
    if timings_url == "":
        return
    if "#" in timings_url:
        timings_url = timings_url.split("#")[0]
    if "?id=" not in timings_url:
        return
    timings_host, timings_id = timings_url.split("?id=")
    timings_json = timings_host + "data.php?id=" + timings_id
    r = requests.get(timings_json).json()

    if r is None:
        embed_var = discord.Embed(title="Timings Analysis", color=0x55ffff)
        embed_var.add_field(name="❌ Invalid report",
                            value="Create a new timings report.",
                            inline=True)
        await message.channel.send(embed=embed_var)
        return

    embed_var = discord.Embed(title="Timings Analysis", color=0x55ffff)
    try:
        version = r["timingsMaster"]["version"]
        online_mode = r["timingsMaster"]["onlinemode"]
        timing_cost = int(r["timingsMaster"]["system"]["timingcost"])
        jvm_version = r["timingsMaster"]["system"]["jvmversion"]
        cpu = int(r["timingsMaster"]["system"]["cpu"])
        flags = r["timingsMaster"]["system"]["flags"]
        plugins = r["timingsMaster"]["plugins"]

        # server.properties
        view_distance = None
        network_compression_threshold = None
        if "Purpur" in version:
            view_distance = int(r["timingsMaster"]["config"]["server.properties"]["view-distance"])
            network_compression_threshold = int(r["timingsMaster"]["config"]["server.properties"]["network-compression-threshold"])

        # bukkit.yml
        ticks_per_monster_spawns = int(r["timingsMaster"]["config"]["bukkit"]["ticks-per"]["monster-spawns"])
        monsters_spawn_limit = int(r["timingsMaster"]["config"]["bukkit"]["spawn-limits"]["monsters"])
        water_ambient_spawn_limit = int(r["timingsMaster"]["config"]["bukkit"]["spawn-limits"]["water-ambient"])
        ambient_spawn_limit = int(r["timingsMaster"]["config"]["bukkit"]["spawn-limits"]["ambient"])
        animals_spawn_limit = int(r["timingsMaster"]["config"]["bukkit"]["spawn-limits"]["animals"])
        water_animals_spawn_limit = int(r["timingsMaster"]["config"]["bukkit"]["spawn-limits"]["water-animals"])
        chunk_gc_period = int(r["timingsMaster"]["config"]["bukkit"]["chunk-gc"]["period-in-ticks"])

        # spigot.yml
        bungeecord = r["timingsMaster"]["config"]["spigot"]["settings"]["bungeecord"]
        save_user_cache_on_stop_only = r["timingsMaster"]["config"]["spigot"]["settings"]["save-user-cache-on-stop-only"]
        mob_spawn_range = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["mob-spawn-range"])
        spigot_view_distance = r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["view-distance"]
        animals_entity_activation_range = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["animals"])
        monsters_entity_activation_range = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["monsters"])
        raiders_entity_activation_range = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["raiders"])
        misc_entity_activation_range = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["misc"])
        water_entity_activation_range = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["water"])
        villagers_entity_activation_range = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["villagers"])
        flying_monsters_entity_activation_range = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["flying-monsters"])
        tick_inactive_villagers = r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["tick-inactive-villagers"]
        nerf_spawner_mobs = r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["nerf-spawner-mobs"]
        wake_up_inactive_villagers_every = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["wake-up-inactive"]["villagers-every"])
        wake_up_inactive_villagers_for = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["wake-up-inactive"]["villagers-every"])
        wake_up_inactive_flying_monsters_for = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["wake-up-inactive"]["villagers-every"])
        wake_up_inactive_animals_every = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["wake-up-inactive"]["villagers-every"])
        wake_up_inactive_villagers_max_per_tick = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["wake-up-inactive"]["villagers-every"])
        wake_up_inactive_animals_for = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["wake-up-inactive"]["villagers-every"])
        wake_up_inactive_monsters_max_per_tick = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["wake-up-inactive"]["villagers-every"])
        wake_up_inactive_flying_monsters_max_per_tick = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["wake-up-inactive"]["villagers-every"])
        wake_up_inactive_flying_monsters_every = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["wake-up-inactive"]["villagers-every"])
        wake_up_inactive_monsters_every = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["wake-up-inactive"]["villagers-every"])
        wake_up_inactive_animals_max_per_tick = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["wake-up-inactive"]["villagers-every"])
        wake_up_inactive_monsters_for = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["wake-up-inactive"]["villagers-every"])
        arrow_despawn_rate = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["arrow-despawn-rate"])
        item_merge_radius = float(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["merge-radius"]["item"])
        exp_merge_radius = float(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["merge-radius"]["exp"])
        max_entity_collisions = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["max-entity-collisions"])

        # paper.yml
        max_auto_save_chunks_per_tick = int(r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["max-auto-save-chunks-per-tick"])
        optimize_explosions = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["optimize-explosions"]
        mob_spawner_tick_rate = int(r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["mob-spawner-tick-rate"])
        disable_chest_cat_detection = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["game-mechanics"]["disable-chest-cat-detection"]
        container_update_tick_rate = int(r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["container-update-tick-rate"])
        grass_spread_tick_rate = int(r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["grass-spread-tick-rate"])
        soft_despawn_range = int(r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["despawn-ranges"]["soft"])
        hard_despawn_range = int(r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["despawn-ranges"]["soft"])
        hopper_disable_move_event = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["hopper"]["disable-move-event"]
        non_player_arrow_despawn_rate = int(r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["non-player-arrow-despawn-rate"])
        creative_arrow_despawn_rate = int(r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["creative-arrow-despawn-rate"])
        prevent_moving_into_unloaded_chunks = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["prevent-moving-into-unloaded-chunks"]
        eigencraft_redstone = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["use-faster-eigencraft-redstone"]
        armor_stands_tick = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["armor-stands-tick"]
        per_player_mob_spawns = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["per-player-mob-spawns"]
        alt_item_despawn_rate_enabled = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["alt-item-despawn-rate"]["enabled"]
        no_tick_view_distance = int(r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["viewdistances"]["no-tick-view-distance"])
        phantoms_only_insomniacs = bool(r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["phantoms-only-attack-insomniacs"])

        if "Yatopia" in version:
            embed_var.add_field(name="⚠ Yatopia",
                                value="Yatopia may be more optimized but it is prone to bugs. "
                                      "Consider using [Purpur](https://ci.pl3x.net/job/Purpur/).",
                                inline=True)
        elif "Paper" in version:
            embed_var.add_field(name="||⚠ Paper||",
                                value="||Purpur has more optimizations but is generally less supported. "
                                      "Consider using [Purpur](https://ci.pl3x.net/job/Purpur/).||",
                                inline=True)
        if "1.16.4" not in version:
            embed_var.add_field(name="⚠ Legacy Build",
                                value="Update to 1.16.4.",
                                inline=True)
        if "-Daikars.new.flags=true" not in flags and "-XX:+UseZGC" not in flags:
            embed_var.add_field(name="⚠ Aikar's Flags",
                                value="Use [Aikar's flags](https://aikar.co/2018/07/02/tuning-the-jvm-g1gc-garbage-collector-flags-for-minecraft/).",
                                inline=True)
        else:
            if "-XX:+PerfDisableSharedMem" not in flags:
                embed_var.add_field(name="⚠ Outdated Flags",
                                value="Add `-XX:+PerfDisableSharedMem` to flags",
                                inline=True)
            if "XX:G1MixedGCCountTarget=4" not in flags:
                embed_var.add_field(name="⚠ Outdated Flags",
                                value="Add `-XX:G1MixedGCCountTarget=4` to flags",
                                inline=True)
        if "-XX:+UseZGC" in flags:
            j_version = int(jvm_version.split(".")[0])
            if j_version < 14:
                embed_var.add_field(name="⚠ ZGC",
                                value="If you are going to use ZGC, you should also use Java 14+.",
                                inline=True)
        if "-Xmx" in flags:
            max_mem = 0
            flaglist = flags.split(" ")
            for flag in flaglist:
                if flag.startswith("-Xmx"):
                    max_mem = flag.split("-Xmx")[1]
                    max_mem = max_mem.replace("G", "000")
                    max_mem = max_mem.replace("M", "")
                    max_mem = max_mem.replace("g", "000")
                    max_mem = max_mem.replace("m", "")
            if int(max_mem) < 5400:
                embed_var.add_field(name="⚠ Low Memory",
                                    value="Allocate at least 6-10GB of ram to your server if you can afford it.",
                                    inline=True)
        if "1.8.0_" in jvm_version:
            embed_var.add_field(name="⚠ Java Version",
                                value="Use Java 11.",
                                inline=True)
        if timing_cost > 400:
            embed_var.add_field(name="⚠ Timingcost",
                                value="Your cpu is overloaded. Find a better host.",
                                inline=True)
        if cpu < 4:
            embed_var.add_field(name="⚠ Cores",
                                value="You have only " + str(cpu) + " core(s). Find a better host.",
                                inline=True)
        if online_mode == "false" and bungeecord == "false":
            embed_var.add_field(name="⚠ online-mode",
                                value="Enable this in server.properties for security.",
                                inline=True)
        if network_compression_threshold == 256:
            if bungeecord == "false":
                embed_var.add_field(name="⚠ network-compression-threshold",
                                    value="Increase this in server.properties. Recommended: 512.",
                                    inline=True)
            else:
                embed_var.add_field(name="⚠ network-compression-threshold",
                                    value="Set this to -1 in server.properties for a bungee server like yours.",
                                    inline=True)

        # Plugins
        if "ClearLag" in plugins:
            embed_var.add_field(name="⚠ ClearLag",
                                value="Plugins that claim to remove lag actually cause more lag. "
                                      "Remove ClearLag.",
                                inline=True)
        if "LagAssist" in plugins:
            embed_var.add_field(name="⚠ LagAssist",
                                value="Plugins that claim to remove lag actually cause more lag. "
                                      "Remove LagAssist.",
                                inline=True)
        if "NoChunkLag" in plugins:
            embed_var.add_field(name="⚠ NoChunkLag",
                                value="Plugins that claim to remove lag actually cause more lag. "
                                      "Remove NoChunkLag.",
                                inline=True)
        if "LimitPillagers" in plugins:
            embed_var.add_field(name="⚠ LimitPillagers",
                                value="You probably don't need LimitPillagers as Paper already adds its features. "
                                      "Remove LimitPillagers.",
                                inline=True)
        if "VillagerOptimizer" in plugins:
            embed_var.add_field(name="⚠ VillagerOptimizer",
                                value="You probably don't need VillagerOptimizer as Paper already adds its features. "
                                      "See entity-activation-range in spigot.yml.",
                                inline=True)
        if "VillagerLobotomizatornator" in plugins and "Purpur" in version:
            embed_var.add_field(name="⚠ LimitPillagers",
                                value="You probably don't need VillagerLobotomizatornator as Purpur already adds its features. "
                                      "Enable villager.lobotomize.enabled in purpur.yml.",
                                inline=True)
        if "StackMob" in plugins:
            embed_var.add_field(name="⚠ StackMob",
                                value="Stacking plugins actually cause more lag. "
                                      "Remove StackMob.",
                                inline=True)
        if "MobStacker" in plugins:
            embed_var.add_field(name="⚠ MobStacker",
                                value="Stacking plugins actually cause more lag. "
                                      "Remove MobStacker.",
                                inline=True)
        if "WildStacker" in plugins:
            embed_var.add_field(name="⚠ WildStacker",
                                value="Stacking plugins actually cause more lag. "
                                      "Remove WildStacker.",
                                inline=True)
        if "SuggestionBlocker" in plugins:
            embed_var.add_field(name="⚠ SuggestionBlocker",
                                value="You probably don't need SuggestionBlocker as Spigot already adds its features. "
                                      "Set tab-complete to -1 in spigot.yml.",
                                inline=True)
        if "FastAsyncWorldEdit" in plugins:
            embed_var.add_field(name="⚠ FastAsyncWorldEdit",
                                value="FAWE can corrupt your world. "
                                      "Consider replacing FAWE with [Worldedit](https://enginehub.org/worldedit/#downloads).",
                                inline=True)
        if "CMI" in plugins:
            embed_var.add_field(name="⚠ CMI",
                                value="CMI is a buggy plugin. "
                                      "Consider replacing CMI with [EssentialsX](https://essentialsx.net/downloads.html).",
                                inline=True)
        if "Spartan" in plugins:
            embed_var.add_field(name="⚠ Spartan",
                                value="Spartan is a laggy anticheat. "
                                      "Consider replacing it with [Matrix](https://matrix.rip/).",
                                inline=True)
        if "IllegalStack" in plugins:
            embed_var.add_field(name="⚠ IllegalStack",
                                value="You probably don't need IllegalStack as Paper already has its features. "
                                      "Remove IllegalStack.",
                                inline=True)
        if "ExploitFixer" in plugins:
            embed_var.add_field(name="⚠ ExploitFixer",
                                value="You probably don't need ExploitFixer as Paper already has its features. "
                                      "Remove ExploitFixer.",
                                inline=True)
        if "EntityTrackerFixer" in plugins:
            embed_var.add_field(name="⚠ EntityTrackerFixer",
                                value="You probably don't need EntityTrackerFixer as Paper already has its features. "
                                      "Remove EntityTrackerFixer.",
                                inline=True)
        if "PhantomSMP" in plugins:
            if phantoms_only_insomniacs:
                embed_var.add_field(name="⚠ PhantomSMP",
                                    value="You probably don't need PhantomSMP as Paper already has its features. "
                                          "Remove PhantomSMP.",
                                    inline=True)
            else:
                embed_var.add_field(name="⚠ PhantomSMP",
                                    value="You probably don't need PhantomSMP as Paper already has its features. "
                                          "Enable phantoms-only-attack-insomniacs in paper.yml",
                                    inline=True)
        if "SilkSpawners" in plugins and "Purpur" in version:
            embed_var.add_field(name="⚠ SilkSpawners",
                                value="You probably don't need SilkSpawners as Purpur already has its features. "
                                      "Remove SilkSpawners.",
                                inline=True)
        if "MineableSpawners" in plugins and "Purpur" in version:
            embed_var.add_field(name="⚠ MineableSpawners",
                                value="You probably don't need MineableSpawners as Purpur already has its features. "
                                      "Remove MineableSpawners.",
                                inline=True)
        if "Orebfuscator" in plugins:
            embed_var.add_field(name="⚠ Orebfuscator",
                                value="You probably don't need Orebfuscator as Paper already has its features. "
                                      "Remove Orebfuscator.",
                                inline=True)
        if "ImageOnMap" in plugins:
            embed_var.add_field(name="⚠ ImageOnMap",
                                value="This plugin has a [memory leak](https://github.com/zDevelopers/ImageOnMap/issues/104). If it is not essential, you should remove it. "
                                      "Consider replacing it with [DrMap](https://www.spigotmc.org/resources/drmap.87368/).",
                                inline=True)
        if "CrazyActions" in plugins:
            embed_var.add_field(name="⚠ CrazyAuctions",
                                value="CrazyAuctions is a laggy plugin. "
                                      "Consider replacing it with [AuctionHouse](https://www.spigotmc.org/resources/auctionhouse.61836/).",
                                inline=True)
        if "GroupManager" in plugins:
            embed_var.add_field(name="⚠ GroupManager",
                                value="GroupManager is an outdated permission plugin. "
                                      "Consider replacing it with [LuckPerms](https://ci.lucko.me/job/LuckPerms/1243/artifact/bukkit/build/libs/LuckPerms-Bukkit-5.2.77.jar).",
                                inline=True)
        if "PermissionsEx" in plugins:
            embed_var.add_field(name="⚠ PermissionsEx",
                                value="PermissionsEx is an outdated permission plugin. "
                                      "Consider replacing it with [LuckPerms](https://ci.lucko.me/job/LuckPerms/1243/artifact/bukkit/build/libs/LuckPerms-Bukkit-5.2.77.jar).",
                                inline=True)
        if "bPermissions" in plugins:
            embed_var.add_field(name="⚠ bPermissions",
                                value="bPermissions is an outdated permission plugin. "
                                      "Consider replacing it with [LuckPerms](https://ci.lucko.me/job/LuckPerms/1243/artifact/bukkit/build/libs/LuckPerms-Bukkit-5.2.77.jar).",
                                inline=True)
        for plugin in plugins:
            if "Songoda" in r["timingsMaster"]["plugins"][plugin]["authors"]:
                embed_var.add_field(name="⚠ " + plugin,
                                    value="This plugin was made by Songoda. You should remove it.",
                                    inline=True)

        if monsters_spawn_limit == 70:
            embed_var.add_field(name="⚠ spawn-limits.monsters",
                                value="Decrease this in bukkit.yml.\nRecommended: 15.",
                                inline=True)
        if animals_spawn_limit == 10:
            embed_var.add_field(name="⚠ spawn-limits.animals",
                                value="Decrease this in bukkit.yml.\nRecommended: 3.",
                                inline=True)
        if water_animals_spawn_limit == 15:
            embed_var.add_field(name="⚠ spawn-limits.water-animals",
                                value="Decrease this in bukkit.yml.\nRecommended: 2.",
                                inline=True)
        if water_ambient_spawn_limit == 20:
            embed_var.add_field(name="⚠ spawn-limits.water-ambient",
                                value="Decrease this in bukkit.yml.\nRecommended: 2.",
                                inline=True)
        if ambient_spawn_limit == 15:
            embed_var.add_field(name="⚠ spawn-limits.ambient",
                                value="Decrease this in bukkit.yml.\nRecommended: 1.",
                                inline=True)
        if chunk_gc_period == 600:
            embed_var.add_field(name="⚠ chunk-gc.period-in-ticks",
                                value="Decrease this in bukkit.yml.\nRecommended: 400.",
                                inline=True)
        if ticks_per_monster_spawns == 1:
            embed_var.add_field(name="⚠ ticks-per.monster-spawns",
                                value="Increase this in bukkit.yml.\nRecommended: 4.",
                                inline=True)
        if view_distance == 10 and spigot_view_distance == "default":
            embed_var.add_field(name="⚠ view-distance",
                                value="Decrease this from default (10) in spigot.yml. "
                                      "Recommended: 3.",
                                inline=True)
        if save_user_cache_on_stop_only == "false":
            embed_var.add_field(name="⚠ save-user-cache-on-stop-only",
                                value="Enable this in spigot.yml.",
                                inline=True)
        if mob_spawn_range == 8 and type(view_distance) == "int" and view_distance < 7 and type(spigot_view_distance) == "int" and spigot_view_distance < 7:
            if spigot_view_distance == -1:
                embed_var.add_field(name="⚠ mob-spawn-range",
                                    value="Decrease this in spigot.yml. "
                                          "Recommended: " + str(view_distance - 1) + ".",
                                    inline=True)
            else:
                embed_var.add_field(name="⚠ mob-spawn-range",
                                    value="Decrease this in spigot.yml. "
                                          "Recommended: " + str(spigot_view_distance - 1) + ".",
                                    inline=True)
        if animals_entity_activation_range == 32:
            embed_var.add_field(name="⚠ entity-activation-range.animals",
                                value="Decrease this in spigot.yml. "
                                      "Recommended: 6.",
                                inline=True)
        if monsters_entity_activation_range == 32:
            embed_var.add_field(name="⚠ entity-activation-range.monsters",
                                value="Decrease this in spigot.yml. "
                                      "Recommended: 16.",
                                inline=True)
        if misc_entity_activation_range == 16:
            embed_var.add_field(name="⚠ entity-activation-range.misc",
                                value="Decrease this in spigot.yml. "
                                      "Recommended: 4.",
                                inline=True)
        if water_entity_activation_range == 16:
            embed_var.add_field(name="⚠ entity-activation-range.water",
                                value="Decrease this in spigot.yml. "
                                      "Recommended: 12.",
                                inline=True)
        if villagers_entity_activation_range == 32:
            embed_var.add_field(name="⚠ entity-activation-range.villagers",
                                value="Decrease this in spigot.yml. "
                                      "Recommended: 16.",
                                inline=True)
        if tick_inactive_villagers == "true":
            embed_var.add_field(name="⚠ tick-inactive-villagers",
                                value="Disable this in spigot.yml.",
                                inline=True)
        if wake_up_inactive_animals_max_per_tick == 4:
            embed_var.add_field(name="⚠ wake-up-inactive.animals-max-per-tick",
                                value="Decrease this in spigot.yml. "
                                      "Recommended: 2.",
                                inline=True)
        if wake_up_inactive_animals_for == 100:
            embed_var.add_field(name="⚠ wake-up-inactive.animals-for",
                                value="Decrease this in spigot.yml. "
                                      "Recommended: 40.",
                                inline=True)
        if wake_up_inactive_monsters_max_per_tick == 8:
            embed_var.add_field(name="⚠ wake-up-inactive.monsters-max-per-tick",
                                value="Decrease this in spigot.yml. "
                                      "Recommended: 4.",
                                inline=True)
        if wake_up_inactive_monsters_for == 100:
            embed_var.add_field(name="⚠ wake-up-inactive.monsters-for",
                                value="Decrease this in spigot.yml. "
                                      "Recommended: 60.",
                                inline=True)
        if wake_up_inactive_villagers_max_per_tick == 4:
            embed_var.add_field(name="⚠ wake-up-inactive.villagers-max-per-tick",
                                value="Decrease this in spigot.yml. "
                                      "Recommended: 1.",
                                inline=True)
        if wake_up_inactive_villagers_for == 100:
            embed_var.add_field(name="⚠ wake-up-inactive.villagers-for",
                                value="Decrease this in spigot.yml. "
                                      "Recommended: 20.",
                                inline=True)
        if wake_up_inactive_flying_monsters_max_per_tick == 8:
            embed_var.add_field(name="⚠ wake-up-inactive.flying-monsters-max-per-tick",
                                value="Decrease this in spigot.yml. "
                                      "Recommended: 1.",
                                inline=True)
        if wake_up_inactive_flying_monsters_for == 100:
            embed_var.add_field(name="⚠ wake-up-inactive.flying-monsters-for",
                                value="Decrease this in spigot.yml. "
                                      "Recommended: 60.",
                                inline=True)
        if item_merge_radius == "true":
            embed_var.add_field(name="⚠ merge-radius.item",
                                value="Increase this in spigot.yml. "
                                      "Recommended: 4.0.",
                                inline=True)
        if exp_merge_radius == "true":
            embed_var.add_field(name="⚠ merge-radius.exp",
                                value="Increase this in spigot.yml. "
                                      "Recommended: 6.0.",
                                inline=True)
        if nerf_spawner_mobs == "false":
            embed_var.add_field(name="⚠ nerf-spawner-mobs",
                                value="Enable this in spigot.yml.",
                                inline=True)
        if arrow_despawn_rate == 1200:
            embed_var.add_field(name="⚠ arrow-despawn-rate",
                                value="Decrease this in spigot.yml. "
                                      "Recommended: 300.",
                                inline=True)
        if max_entity_collisions == 8:
            embed_var.add_field(name="⚠ max-entity-collisions",
                                value="Decrease this in spigot.yml. "
                                      "Recommended: 2.",
                                inline=True)
        if max_auto_save_chunks_per_tick == 24:
            embed_var.add_field(name="⚠ max-auto-save-chunks-per-tick",
                                value="Decrease this in paper.yml. "
                                      "Recommended: 6.",
                                inline=True)
        if optimize_explosions == "false":
            embed_var.add_field(name="⚠ optimize-explosions",
                                value="Enable this in paper.yml.",
                                inline=True)
        if mob_spawner_tick_rate == 1:
            embed_var.add_field(name="⚠ mob-spawner-tick-rate",
                                value="Increase this in paper.yml. "
                                      "Recommended: 2.",
                                inline=True)
        if disable_chest_cat_detection == "false":
            embed_var.add_field(name="⚠ disable_chest_cat_detection",
                                value="Enable this in paper.yml.",
                                inline=True)
        if container_update_tick_rate == "false":
            embed_var.add_field(name="⚠ container-update-tick-rate",
                                value="Increase this in paper.yml. "
                                      "Recommended: 3.",
                                inline=True)
        if grass_spread_tick_rate == 1:
            embed_var.add_field(name="⚠ grass-spread-tick-rate",
                                value="Increase this in paper.yml. "
                                      "Recommended: 4",
                                inline=True)
        if soft_despawn_range == 32:
            embed_var.add_field(name="⚠ despawn-ranges.soft",
                                value="Decrease this in paper.yml. "
                                      "Recommended: 28",
                                inline=True)
        if hard_despawn_range == 128:
            embed_var.add_field(name="⚠ despawn-ranges.hard",
                                value="Decrease this in paper.yml. "
                                      "Recommended: 96",
                                inline=True)
        if hopper_disable_move_event == "false":
            embed_var.add_field(name="⚠ hopper.disable-move-event",
                                value="Enable this in paper.yml.",
                                inline=True)
        if non_player_arrow_despawn_rate == -1:
            embed_var.add_field(name="⚠ non-player-arrow-despawn-rate",
                                value="Set a value in paper.yml. "
                                      "Recommended: 60",
                                inline=True)
        if creative_arrow_despawn_rate == -1:
            embed_var.add_field(name="⚠ creative-arrow-despawn-rate",
                                value="Set a value in paper.yml. "
                                      "Recommended: 60",
                                inline=True)
        if prevent_moving_into_unloaded_chunks == "false":
            embed_var.add_field(name="⚠ prevent-moving-into-unloaded-chunks",
                                value="Enable this in paper.yml.",
                                inline=True)
        if eigencraft_redstone == "false":
            embed_var.add_field(name="⚠ use-faster-eigencraft-redstone",
                                value="Enable this in paper.yml.",
                                inline=True)
        if armor_stands_tick == "true" and "PetBlocks" not in plugins and "BlockBalls" not in plugins and "ArmorStandTools" not in plugins:
            embed_var.add_field(name="⚠ armor-stands-tick",
                                value="Disable this in paper.yml.",
                                inline=True)
        if per_player_mob_spawns == "false":
            embed_var.add_field(name="⚠ per-player-mob-spawns",
                                value="Enable this in paper.yml.",
                                inline=True)
        if alt_item_despawn_rate_enabled == "false":
            embed_var.add_field(name="⚠ alt-item-despawn-rate.enabled",
                                value="Enable this in paper.yml.",
                                inline=True)
        if "Purpur" in version:
            use_alternate_keepalive = r["timingsMaster"]["config"]["purpur"]["settings"]["use-alternate-keepalive"]
            dont_send_useless_entity_packets = r["timingsMaster"]["config"]["purpur"]["settings"]["dont-send-useless-entity-packets"]
            disable_treasure_searching = r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["mobs"]["dolphin"]["disable-treasure-searching"]
            brain_ticks = int(r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["mobs"]["villager"]["brain-ticks"])
            iron_golem_radius = int(r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["mobs"]["villager"]["spawn-iron-golem"]["radius"])
            iron_golem_limit = int(r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["mobs"]["villager"]["spawn-iron-golem"]["limit"])
            aggressive_towards_villager_when_lagging = r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["mobs"]["zombie"]["aggressive-towards-villager-when-lagging"]
            entities_can_use_portals = r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["gameplay-mechanics"]["entities-can-use-portals"]
            lobotomize_enabled = r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["mobs"]["villager"]["lobotomize"]["enabled"]

            if no_tick_view_distance == -1:
                if spigot_view_distance != "default" or view_distance != 10:
                    if spigot_view_distance == "default" and view_distance > 3:
                        embed_var.add_field(name="⚠ no-tick-view-distance",
                                            value="Set a value in paper.yml. "
                                                  "Recommended: " + str(view_distance) + ". And reduce view-distance in server.properties. Recommended: 3.",
                                            inline=True)
                    elif type(spigot_view_distance) == "int" and int(spigot_view_distance) > 3:
                        embed_var.add_field(name="⚠ no-tick-view-distance",
                                            value="Set a value in paper.yml. "
                                                  "Recommended: " + str(spigot_view_distance) + ". And reduce view-distance in spigot.yml. Recommended: 3.",
                                            inline=True)
            if use_alternate_keepalive == "false" and "TCPShield" not in plugins:
                embed_var.add_field(name="⚠ use-alternate-keepalive",
                                    value="Enable this in purpur.yml.",
                                    inline=True)
            if use_alternate_keepalive == "true" and "TCPShield" in plugins:
                embed_var.add_field(name="⚠ use-alternate-keepalive",
                                    value="Disable this in purpur.yml.",
                                    inline=True)
            if dont_send_useless_entity_packets == "false":
                embed_var.add_field(name="⚠ dont-send-useless-entity-packets",
                                    value="Enable this in purpur.yml.",
                                    inline=True)
            if disable_treasure_searching == "false":
                embed_var.add_field(name="⚠ dolphin.disable-treasure-searching",
                                    value="Enable this in purpur.yml.",
                                    inline=True)
            if brain_ticks == 1:
                embed_var.add_field(name="⚠ villager.brain-ticks",
                                    value="Increase this in purpur.yml. "
                                          "Recommended: 4.",
                                    inline=True)
            if iron_golem_radius == 0:
                embed_var.add_field(name="⚠ spawn-iron-golem.radius",
                                    value="Set a value in purpur.yml. "
                                          "Recommended: 32.",
                                    inline=True)
            if iron_golem_limit == 0:
                embed_var.add_field(name="⚠ spawn-iron-golem.limit",
                                    value="Set a value in purpur.yml. "
                                          "Recommended: 5.",
                                    inline=True)
            if aggressive_towards_villager_when_lagging == "true":
                embed_var.add_field(name="⚠ zombie.aggresive-towards-villager-when-lagging",
                                    value="Disable this in purpur.yml.",
                                    inline=True)
            if entities_can_use_portals == "true":
                embed_var.add_field(name="⚠ entities-can-use-portals",
                                    value="Disable this in purpur.yml to prevent players from creating chunk anchors.",
                                    inline=True)
            if lobotomize_enabled == "false":
                embed_var.add_field(name="⚠ villager.lobotomize.enabled",
                                    value="Enable this in purpur.yml.",
                                    inline=True)

        if len(embed_var.fields) == 0:
            embed_var.add_field(name="✅ All good",
                                value="Analyzed with no issues")
            await message.channel.send(embed=embed_var)
            return
        issue_count = len(embed_var.fields)
        if issue_count > 25:
            embed_var.description = "Showing 25 of " + str(issue_count) + " recommendations."
        else:
            embed_var.description = "Showing " + str(issue_count) + " of " + str(issue_count) + " recommendations."
    except KeyError:
        embed_var.add_field(name="⚠ Outdated",
                        value="Please update.",
                        inline=True)

    await message.channel.send(embed=embed_var)


@bot.event
async def on_ready():
    # Marks bot as running
    logging.info('I am running.')


@bot.event
async def on_message(message):
    # Account link
    if message.author != bot.user and message.guild == None:
        channel = message.channel
        global cookies
        await channel.send("Processing, please wait...")
        # Potential API key, so tries it out
        if len(message.content) == 48:
            url = "https://panel.birdflop.com/api/client/account"

            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + message.content,
            }

            response = requests.get(url, headers=headers, cookies=cookies)

            # If API token is verified to be correct:
            if str(response) == "<Response [200]>":

                # Formats response of account in JSON format
                json_response = response.json()

                # Loads contents of users.json
                file = open('users.json', 'r')
                data = json.load(file)
                file.close()

                # Checks if user exists. If so, skips adding them to users.json
                client_id_already_exists = False
                discord_id_already_exists = False
                for user in data['users']:
                    if user['client_id'] == json_response['attributes']['id']:
                        client_id_already_exists = True
                        logging.info("Client ID already exists")
                    if user['discord_id'] == message.author.id:
                        discord_id_already_exists = True
                        logging.info("Discord ID already exists")
                if client_id_already_exists == False and discord_id_already_exists == False:
                    data['users'].append({
                        'discord_id': message.author.id,
                        'client_id': json_response['attributes']['id'],
                        'client_api_key': message.content
                    })
                    json_dumps = json.dumps(data, indent=2)
                    # Adds user to users.json
                    file = open('users.json', 'w')
                    file.write(json_dumps)
                    file.close()

                    guild = bot.get_guild(guild_id)
                    member = guild.get_member(message.author.id)
                    if member:

                        url = "https://panel.birdflop.com/api/client"

                        headers = {
                            'Accept': 'application/json',
                            'Authorization': 'Bearer ' + message.content,
                        }

                        response = requests.get(url, headers=headers, cookies=cookies)

                        # If API token is verified to be correct, continues
                        if str(response) == "<Response [200]>":

                            # Formats response for servers in JSON format
                            servers_json_response = response.json()

                            user_client = False
                            user_subuser = False
                            user_crabwings = False
                            user_duckfeet = False
                            user_elktail = False
                            for server in servers_json_response['data']:
                                server_owner = server['attributes']['server_owner']
                                if server_owner == True:
                                    user_client = True
                                elif server_owner == False:
                                    user_subuser = True
                                server_node = server['attributes']['node']
                                if server_node == "Crabwings - NYC":
                                    user_crabwings = True
                                elif server_node == "Duckfeet - EU":
                                    user_duckfeet = True
                                elif server_node == "Elktail - EU":
                                    user_elktail = True
                            if user_client == True:
                                role = discord.utils.get(guild.roles, id=client_role_id)
                                await member.add_roles(role)
                            if user_subuser == True:
                                role = discord.utils.get(guild.roles, id=subuser_role_id)
                                await member.add_roles(role)
                            if user_crabwings == True:
                                role = discord.utils.get(guild.roles, id=crabwings_role_id)
                                await member.add_roles(role)
                            if user_duckfeet == True:
                                role = discord.utils.get(guild.roles, id=duckfeet_role_id)
                                await member.add_roles(role)
                            if user_elktail == True:
                                role = discord.utils.get(guild.roles, id=elktail_role_id)
                                await member.add_roles(role)
                            role = discord.utils.get(guild.roles, id=verified_role_id)
                            await member.add_roles(role)

                    await channel.send(
                        'Your Discord account has been linked to your panel account! You may unlink your Discord and panel accounts by reacting in the #verification channel or by deleting your Verification API key.')
                    logging.info("Success message sent to " + message.author.name + "#" + str(
                        message.author.discriminator) + " (" + str(
                        message.author.id) + ")" + ". User linked to API key " + message.content + " and client_id " + str(
                        json_response['attributes']['id']))
                elif discord_id_already_exists:
                    await channel.send(
                        'Sorry, your Discord account is already linked to a panel account. If you would like to link your Discord account to a different panel account, please unlink your Discord account first by reacting in the #verification channel.')
                    logging.info("Duplicate Discord message sent to " + message.author.name + "#" + str(
                        message.author.discriminator) + " (" + str(
                        message.author.id) + ")" + " for using API key " + message.content + " linked to client_id " + str(
                        json_response['attributes']['id']))
                elif client_id_already_exists:
                    await channel.send(
                        'Sorry, your panel account is already linked to a Discord account. If you would like to link your panel account to a different Discord account, please unlink your panel account first by deleting its Verification API key and waiting up to 10 minutes.')
                    logging.info("Duplicate panel message sent to " + message.author.name + "#" + str(
                        message.author.discriminator) + " (" + str(
                        message.author.id) + ")" + " for using API key " + message.content + " linked to client_id " + str(
                        json_response['attributes']['id']))
            else:
                # Says if API key is the corect # of characters but invalid
                await channel.send("Sorry, that appears to be an invalid API key.")
                logging.info(
                    'invalid sent to ' + message.author.name + "#" + str(message.author.discriminator) + " (" + str(
                        message.author.id) + ")")
        else:
            # Says this if API key is incorrect # of characters
            await channel.send(
                'Sorry, that doesn\'t appear to be an API token. An API token should be a long string resembling this: ```yQSB12ik6YRcmE4d8tIEj5gkQqDs6jQuZwVOo4ZjSGl28d46```')
            logging.info("obvious incorrect sent to " + message.author.name + "#" + str(
                message.author.discriminator) + " (" + str(message.author.id) + ")")

    # Binflop
    elif len(message.attachments) > 0:
        if message.attachments[0].url.endswith(
                ('.png', '.jpg', '.jpeg', '.mp4', '.mov', '.avi', '.gif', '.image')) == False:
            download = message.attachments[0].url
            r = requests.get(download, allow_redirects=True)
            text = r.text
            text = "\n".join(text.splitlines())
            if '�' not in text:  # If it's not an image/gif
                truncated = False
                if len(text) > 100000:
                    text = text[:99999]
                    truncated = True
                req = requests.post('https://bin.birdflop.com/documents', data=text)
                key = json.loads(req.content)['key']
                response = ""
                response = response + "https://bin.birdflop.com/" + key
                response = response + "\nRequested by " + message.author.mention
                if truncated:
                    response = response + "\n(file was truncated because it was too long.)"
                embed_var = discord.Embed(title="Please use a paste service", color=0x1D83D4)
                embed_var.description = response
                await message.channel.send(embed=embed_var)

    await analyze_timings(message)

    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload):
    global verification_message
    global verification_channel
    if payload.message_id != verification_message:
        return
    if payload.user_id == bot.user.id:
        return
    # Remove the reaction
    guild = discord.utils.get(bot.guilds, id=guild_id)
    verification_channel_obj = await bot.fetch_channel(verification_channel)
    verification_message_obj = await verification_channel_obj.fetch_message(verification_message)
    member = guild.get_member(payload.user_id)
    await verification_message_obj.remove_reaction(payload.emoji, member)
    if str(payload.emoji) == "✅":
        await member.send(
            "Hey there! It looks like you'd like to verify your account. I'm here to help you with that!\n\nIf you're confused at any point, see https://birdflop.com/verification for a tutorial.\n\nWith that said, let's get started! You'll want to start by grabbing some API credentials for your account by signing into https://panel.birdflop.com. Head over to the **Account** section in the top right, then click on the **API Credentials tab**. You'll want to create an API key with description `Verification` and `172.18.0.2` in the **Allowed IPs section**.\n\nWhen you finish entering the necessary information, hit the blue **Create **button.\n\nNext, you'll want to copy your API credentials. After clicking **Create**, you'll receive a long string. Copy it with `ctrl+c` (`cmnd+c` on Mac) or by right-clicking it and selecting **Copy**.\n\nIf you click on the **Close **button before copying the API key, no worries! Delete your API key and create a new one with the same information.\n\nFinally, direct message your API key to Botflop: that's me!\n\nTo verify that you are messaging the key to the correct user, please ensure that the my ID is `Botflop#2403` and that my username is marked with a blue **BOT** badge. Additionally, the only server under the **Mutual Servers** tab should be Birdflop Hosting.\n\nAfter messaging me your API key, you should receive a success message. If you do not receive a success message, please create a ticket in the Birdflop Discord's #support channel.")
        logging.info("sent verification challenge to " + member.name + "#" + str(member.discriminator) + " (" + str(
            member.id) + ")")
    else:
        file = open('users.json', 'r')
        data = json.load(file)
        file.close()
        i = 0
        j = -1
        for client in data['users']:
            j += 1
            if client['discord_id'] == member.id:
                data['users'].pop(j)
                i = 1
        if i == 1:
            json_dumps = json.dumps(data, indent=2)
            file = open('users.json', 'w')
            file.write(json_dumps)
            file.close()
            await member.edit(roles=[])
            await member.send("Your Discord account has successfully been unlinked from your Panel account!")
            logging.info(
                'successfully unlinked ' + member.name + "#" + str(member.discriminator) + " (" + str(member.id) + ")")


@bot.command()
async def ping(ctx):
    await ctx.send(f'Your ping is {round(bot.latency * 1000)}ms')


@bot.command(name="react", pass_context=True)
@has_permissions(administrator=True)
async def react(ctx, url, reaction):
    channel = await bot.fetch_channel(int(url.split("/")[5]))
    message = await channel.fetch_message(int(url.split("/")[6]))
    await message.add_reaction(reaction)
    logging.info('reacted to ' + url + ' with ' + reaction)


@tasks.loop(minutes=10)
async def updater():
    global cookies
    logging.info("Synchronizing roles")
    file = open('users.json', 'r')
    data = json.load(file)
    file.close()
    guild = bot.get_guild(guild_id)
    i = -1
    for client in data['users']:
        i += 1
        member = guild.get_member(client['discord_id'])
        if member:
            api_key = client['client_api_key']
            url = "https://panel.birdflop.com/api/client"
            headers = {
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + api_key,
            }
            response = requests.get(url, headers=headers, cookies=cookies)

            # If API token is verified to be correct, continues
            if str(response) == "<Response [200]>":
                # Formats response for servers in JSON format
                servers_json_response = response.json()

                user_client = False
                user_subuser = False
                user_crabwings = False
                user_duckfeet = False
                user_elktail = False
                for server in servers_json_response['data']:
                    server_owner = server['attributes']['server_owner']
                    if server_owner == True:
                        user_client = True
                    elif server_owner == False:
                        user_subuser = True
                    server_node = server['attributes']['node']
                    if server_node == "Crabwings - NYC":
                        user_crabwings = True
                    elif server_node == "Duckfeet - EU":
                        user_duckfeet = True
                    elif server_node == "Elktail - EU":
                        user_elktail = True
                role = discord.utils.get(guild.roles, id=client_role_id)
                if user_client == True:
                    await member.add_roles(role)
                else:
                    await member.remove_roles(role)
                role = discord.utils.get(guild.roles, id=subuser_role_id)
                if user_subuser == True:
                    await member.add_roles(role)
                else:
                    await member.remove_roles(role)
                role = discord.utils.get(guild.roles, id=crabwings_role_id)
                if user_crabwings == True:
                    await member.add_roles(role)
                else:
                    await member.remove_roles(role)
                role = discord.utils.get(guild.roles, id=duckfeet_role_id)
                if user_duckfeet == True:
                    await member.add_roles(role)
                else:
                    await member.remove_roles(role)
                role = discord.utils.get(guild.roles, id=elktail_role_id)
                if user_elktail == True:
                    await member.add_roles(role)
                else:
                    await member.remove_roles(role)
            else:
                data['users'].pop(i)
                json_dumps = json.dumps(data, indent=2)
                file = open('users.json', 'w')
                file.write(json_dumps)
                file.close()
                await member.edit(roles=[])
                logging.info("removed discord_id " + str(client['discord_id']) + " with client_id " + str(
                    client['client_id']) + " and INVALID client_api_key " + client['client_api_key'])
        else:
            data['users'].pop(i)
            json_dumps = json.dumps(data, indent=2)
            file = open('users.json', 'w')
            file.write(json_dumps)
            file.close()
            logging.info("removed discord_id " + str(client['discord_id']) + " with client_id " + str(
                client['client_id']) + " and client_api_key " + client['client_api_key'])

    # Update backups
    logging.info('Ensuring backups')
    url = "https://panel.birdflop.com/api/application/servers"

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + application_api_key,
    }
    response = requests.get(url, headers=headers, cookies=cookies)
    servers_json_response = response.json()

    file = open('modified_servers.json', 'r')
    modified_servers = json.load(file)
    file.close()

    i = -1

    for server in servers_json_response['data']:
        i += 1
        already_exists = False
        for server2 in modified_servers['servers']:
            if already_exists == False:
                if server['attributes']['uuid'] == server2['uuid']:
                    already_exists = True
        if already_exists == False:
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + application_api_key,
            }

            data = '{ "allocation": ' + str(server['attributes']['allocation']) + ', "memory": ' + str(
                server['attributes']['limits']['memory']) + ', "swap": 0, "disk": ' + str(
                server['attributes']['limits']['disk']) + ', "io": ' + str(
                server['attributes']['limits']['io']) + ', "cpu": ' + str(
                server['attributes']['limits']['cpu']) + ', "threads": null, "feature_limits": { "databases": ' + str(
                server['attributes']['feature_limits']['databases']) + ', "allocations": ' + str(
                server['attributes']['feature_limits']['allocations']) + ', "backups": 3 } }'

            response = requests.patch(
                'https://panel.birdflop.com/api/application/servers/' + str(server['attributes']['id']) + '/build',
                headers=headers, cookies=cookies, data=data)

            if (str(response)) == "<Response [200]>":
                modified_servers['servers'].append({
                    'uuid': str(server['attributes']['uuid'])
                })

                file = open('modified_servers.json', 'w')
                json_dumps = json.dumps(modified_servers, indent=2)
                file.write(json_dumps)
                file.close()

                logging.info("modified " + str(server['attributes']['name']) + ' with data ' + data)
            else:
                logging.info("failed to modify " + str(server['attributes']['name']) + ' with data ' + data)


# Plugin Updater
# @bot.command()
# async def update(ctx, server, plugin):
#    command_discord_id = ctx.message.author.id
#    await ctx.send (f'your discord ID is {command_discord_id}')
#    file = open('users.json', 'r')
#    data = json.load(file)
#    file.close()
#    i=-1
#    for client in data['users']:
#        if i==-1:
#            if client["discord_id"] == command_discord_id:
#                i=0
#                command_client_id = client["client_id"]
#                command_client_api_key = client["client_api_key"]
#    if i==-1:
#        await ctx.send("You must be verified to use this command.")
#    else:
#        if plugin.lower() == "votingplugin":
#            subprocess.call(['java', '-jar', 'spiget-downloader.jar', '--url', 'https://www.spigotmc.org/resources/votingplugin.15358/download?version=373388', '--file', 'ProtocolLib.jar'])

#
#            print("Finding latest VotingPlugin")
#
#            headers = {
#              "cache-control": "max-age=1800",
#              "content-type": "application/json; charset=utf-8"
#            }
#
#            response = requests.get("https://api.spiget.org/v2/resources/15358/versions/latest")
#            spiget_json = response.json()
#            print("Latest Version = " + str(spiget_json["id"]))
#
#            url = "https://www.spigotmc.org/resources/votingplugin.15358/download?version=373388"
#            headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}
#            r = requests.get(url, headers=headers)
#            open('VotingPlugin1.jar', 'wb').write(r.content)
#
#
#            #urllib.request.urlretrieve("https://api.spiget.org/v2/resources/15358/versions/373388/download",'/home/container/zzzcache/VotingPlugin1.jar')
#            #urllib.request.urlretrieve("https://www.spigotmc.org/resources/votingplugin.15358/download?version=373388",'/home/container/zzzcache/VotingPlugin2.jar')
#
#
#            global cookies
#
#            headers = {
#                'Accept': 'application/json',
#                'Content-Type': 'application/json',
#                'Authorization': 'Bearer ' + command_client_api_key,
#            }
#
#            response = requests.get(f'https://panel.birdflop.com/api/client/servers/{server}/files/upload', headers=headers, cookies=cookies)
#            print(str(response))
#            update_json = response.json()
#            transfer_url = update_json["attributes"]["url"]
#            print(transfer_url)
#        else:
#            await ctx.send("Sorry, that is not a valid plugin.")


@updater.before_loop
async def before_updater():
    logging.info('waiting to enter loop')
    await bot.wait_until_ready()


updater.start()
bot.run(token)

# full name: message.author.name + "#" + str(message.author.discriminator) + " (" + str(message.author.id) + ")"
