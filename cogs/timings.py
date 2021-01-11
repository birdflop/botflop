import discord
from discord.ext import commands
import requests

class Timings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Use @commands.Cog.listener() instead of event and use @commands.command() for commands

    async def analyze_timings(self, message):
        enterless_message = message.content.replace("\n", " ")
        words = enterless_message.split(" ")
        timings_url = ""
        for word in words:
            if word.startswith("https://timings.") and "/?id=" in word:
                timings_url = word
                break
            if word.startswith("https://www.spigotmc.org/go/timings?url=") or word.startswith(
                    "https://timings.spigotmc.org/?url="):
                embed_var = discord.Embed(title="Timings Analysis", color=0x55ffff)
                embed_var.add_field(name="❌ Spigot",
                                    value="Upgrade to [Purpur](https://ci.pl3x.net/job/Purpur/).")
                embed_var.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                embed_var.url = timings_url
                await message.reply(embed=embed_var)
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
                                value="Create a new timings report.")
            embed_var.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            embed_var.url = timings_url
            await message.reply(embed=embed_var)
            return

        embed_var = discord.Embed(title="Timings Analysis", color=0x55ffff)
        embed_var.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
        embed_var.url = timings_url
        unchecked = 0
        try:
            try:
                version = r["timingsMaster"]["version"]
                if "1.16.4" not in version:
                    embed_var.add_field(name="❌ Legacy Build",
                                        value="Update to 1.16.4.")
                using_yatopia = "yatopia" in r["timingsMaster"]["config"]
                if using_yatopia:
                    embed_var.add_field(name="❌ Yatopia",
                                        value="Yatopia is prone to bugs. "
                                              "Consider using [Purpur](https://ci.pl3x.net/job/Purpur/).")
                elif "Paper" in version:
                    embed_var.add_field(name="||❌ Paper||",
                                        value="||Purpur has more optimizations but is generally less supported. "
                                              "Consider using [Purpur](https://ci.pl3x.net/job/Purpur/).||")
            except KeyError:
                unchecked = unchecked + 1

            try:
                online_mode = r["timingsMaster"]["onlinemode"]
                bungeecord = r["timingsMaster"]["config"]["spigot"]["settings"]["bungeecord"]
                velocity_online_mode = r["timingsMaster"]["config"]["paper"]["settings"]["velocity-support"]["online-mode"]
                velocity_enabled = r["timingsMaster"]["config"]["paper"]["settings"]["velocity-support"]["enabled"]

                if not online_mode and bungeecord == "false" and (velocity_online_mode == "false" or velocity_enabled == "false"):
                    embed_var.add_field(name="❌ online-mode",
                                        value="Enable this in server.properties for security.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                timing_cost = int(r["timingsMaster"]["system"]["timingcost"])
                if timing_cost > 300:
                    embed_var.add_field(name="❌ Timingcost",
                                        value="Your timingcost is " + str(timing_cost) + ". Find a [better host](https://www.birdflop.com).")
            except KeyError:
                unchecked = unchecked + 1

            try:
                jvm_version = r["timingsMaster"]["system"]["jvmversion"]
                if jvm_version.startswith("1.8.") or jvm_version.startswith("9.") or jvm_version.startswith("10."):
                    embed_var.add_field(name="❌ Java Version",
                                        value="You are using Java " + jvm_version + ". Update to [Java 11](https://adoptopenjdk.net/installation.html).")
            except KeyError:
                unchecked = unchecked + 1

            try:
                flags = r["timingsMaster"]["system"]["flags"]
                if "-XX:+UseZGC" in flags:
                    jvm_version = r["timingsMaster"]["system"]["jvmversion"]
                    java_version = jvm_version.split(".")[0]
                    if int(java_version) < 14:
                        embed_var.add_field(name="❌ Java " + java_version,
                                            value="If you are going to use ZGC, you should also use Java 14+.")
                elif "-Daikars.new.flags=true" in flags:
                    if "-XX:+PerfDisableSharedMem" not in flags:
                        embed_var.add_field(name="❌ Outdated Flags",
                                            value="Add `-XX:+PerfDisableSharedMem` to flags")
                    if "XX:G1MixedGCCountTarget=4" not in flags:
                        embed_var.add_field(name="❌ Outdated Flags",
                                            value="Add `-XX:G1MixedGCCountTarget=4` to flags")
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
                            embed_var.add_field(name="❌ Low Memory",
                                                value="Allocate at least 6-10GB of ram to your server if you can afford it.")
                        if "-Xms" in flags:
                            min_mem = 0
                            flaglist = flags.split(" ")
                            for flag in flaglist:
                                if flag.startswith("-Xms"):
                                    min_mem = flag.split("-Xms")[1]
                                    min_mem = min_mem.replace("G", "000")
                                    min_mem = min_mem.replace("M", "")
                                    min_mem = min_mem.replace("g", "000")
                                    min_mem = min_mem.replace("m", "")
                            if min_mem != max_mem:
                                embed_var.add_field(name="❌ Aikar's Flags",
                                                    value="Your Xmx and Xms values should be equivalent when using Aikar's flags.")
                elif "-Dusing.aikars.flags=mcflags.emc.gs" in flags:
                    embed_var.add_field(name="❌ Outdated Flags",
                                        value="Update [Aikar's flags](https://aikar.co/2018/07/02/tuning-the-jvm-g1gc-garbage-collector-flags-for-minecraft/).")
                else:
                    embed_var.add_field(name="❌ Aikar's Flags",
                                        value="Use [Aikar's flags](https://aikar.co/2018/07/02/tuning-the-jvm-g1gc-garbage-collector-flags-for-minecraft/).")
            except KeyError:
                unchecked = unchecked + 1
            try:
                cpu = int(r["timingsMaster"]["system"]["cpu"])
                if cpu == 1:
                    embed_var.add_field(name="❌ Threads",
                                        value="You have only " + str(cpu) + " thread. Find a [better host](https://www.birdflop.com).")
                if cpu == 2:
                    embed_var.add_field(name="❌ Threads",
                                        value="You have only " + str(cpu) + " threads. Find a [better host](https://www.birdflop.com).")
            except KeyError:
                unchecked = unchecked + 1

            try:
                plugins = r["timingsMaster"]["plugins"]
                if "ClearLag" in plugins:
                    embed_var.add_field(name="❌ ClearLag",
                                        value="Plugins that claim to remove lag actually cause more lag. "
                                              "Remove ClearLag.")
                if "LagAssist" in plugins:
                    embed_var.add_field(name="❌ LagAssist",
                                        value="LagAssist should only be used for analytics and preventative measures."
                                              "All other features of the plugin should be disabled.")
                if "NoChunkLag" in plugins:
                    embed_var.add_field(name="❌ NoChunkLag",
                                        value="Plugins that claim to remove lag actually cause more lag. "
                                              "Remove NoChunkLag.")
                if "ServerBooster" in plugins:
                    embed_var.add_field(name="❌ ServerBooster",
                                        value="Plugins that claim to remove lag actually cause more lag. "
                                              "Remove ServerBooster.")
                if "MobLimiter" in plugins:
                    embed_var.add_field(name="❌ MobLimiter",
                                        value="You probably don't need MobLimiter as Bukkit already has its features. "
                                              "Remove MobLimiter.")
                if "BookLimiter" in plugins:
                    embed_var.add_field(name="❌ BookLimiter",
                                        value="You probably don't need BookLimiter as Paper already has its features. "
                                              "Remove BookLimiter.")
                if "LimitPillagers" in plugins:
                    embed_var.add_field(name="❌ LimitPillagers",
                                        value="You probably don't need LimitPillagers as Paper already adds its features. "
                                              "Remove LimitPillagers.")
                if "VillagerOptimiser" in plugins:
                    embed_var.add_field(name="❌ VillagerOptimiser",
                                        value="You probably don't need VillagerOptimiser as Paper already adds its features. "
                                              "See entity-activation-range in spigot.yml.")
                if "StackMob" in plugins:
                    embed_var.add_field(name="❌ StackMob",
                                        value="Stacking plugins actually cause more lag. "
                                              "Remove StackMob.")
                if "Stacker" in plugins:
                    embed_var.add_field(name="❌ Stacker",
                                        value="Stacking plugins actually cause more lag. "
                                              "Remove Stacker.")
                if "MobStacker" in plugins:
                    embed_var.add_field(name="❌ MobStacker",
                                        value="Stacking plugins actually cause more lag. "
                                              "Remove MobStacker.")
                if "WildStacker" in plugins:
                    embed_var.add_field(name="❌ WildStacker",
                                        value="Stacking plugins actually cause more lag. "
                                              "Remove WildStacker.")
                if "SuggestionBlocker" in plugins:
                    embed_var.add_field(name="❌ SuggestionBlocker",
                                        value="You probably don't need SuggestionBlocker as Spigot already adds its features. "
                                              "Set tab-complete to -1 in spigot.yml.")
                if "FastAsyncWorldEdit" in plugins:
                    embed_var.add_field(name="❌ FastAsyncWorldEdit",
                                        value="FAWE can corrupt your world. "
                                              "Consider replacing FAWE with [Worldedit](https://enginehub.org/worldedit/#downloads).")
                if "CMI" in plugins:
                    embed_var.add_field(name="❌ CMI",
                                        value="CMI is a buggy plugin. "
                                              "Consider replacing CMI with [EssentialsX](https://essentialsx.net/downloads.html).")
                if "Spartan" in plugins:
                    embed_var.add_field(name="❌ Spartan",
                                        value="Spartan is a laggy anticheat. "
                                              "Consider replacing it with [Matrix](https://matrix.rip/), [NCP](https://ci.codemc.io/job/Updated-NoCheatPlus/job/Updated-NoCheatPlus/), or [AAC](https://www.spigotmc.org/resources/aac-advanced-anti-cheat-hack-kill-aura-blocker.6442/).")
                if "IllegalStack" in plugins:
                    embed_var.add_field(name="❌ IllegalStack",
                                        value="You probably don't need IllegalStack as Paper already has its features. "
                                              "Remove IllegalStack.")
                if "ExploitFixer" in plugins:
                    embed_var.add_field(name="❌ ExploitFixer",
                                        value="You probably don't need ExploitFixer as Paper already has its features. "
                                              "Remove ExploitFixer.")
                if "EntityTrackerFixer" in plugins:
                    embed_var.add_field(name="❌ EntityTrackerFixer",
                                        value="You probably don't need EntityTrackerFixer as Paper already has its features. "
                                              "Remove EntityTrackerFixer.")
                if "Orebfuscator" in plugins:
                    embed_var.add_field(name="❌ Orebfuscator",
                                        value="You probably don't need Orebfuscator as Paper already has its features. "
                                              "Remove Orebfuscator.")
                if "ImageOnMap" in plugins:
                    embed_var.add_field(name="❌ ImageOnMap",
                                        value="This plugin has a [memory leak](https://github.com/zDevelopers/ImageOnMap/issues/104). If it is not essential, you should remove it. "
                                              "Consider replacing it with [an alternative](https://www.spigotmc.org/resources/drmap.87368/).")
                if "CrazyActions" in plugins:
                    embed_var.add_field(name="❌ CrazyAuctions",
                                        value="CrazyAuctions is a laggy plugin, even according to the developer. "
                                              "Consider replacing it with [AuctionHouse](https://www.spigotmc.org/resources/auctionhouse.61836/).")
                if "GroupManager" in plugins:
                    embed_var.add_field(name="❌ GroupManager",
                                        value="GroupManager is an outdated permission plugin. "
                                              "Consider replacing it with [LuckPerms](https://ci.lucko.me/job/LuckPerms/1243/artifact/bukkit/build/libs/LuckPerms-Bukkit-5.2.77.jar).")
                if "PermissionsEx" in plugins:
                    embed_var.add_field(name="❌ PermissionsEx",
                                        value="PermissionsEx is an outdated permission plugin. "
                                              "Consider replacing it with [LuckPerms](https://ci.lucko.me/job/LuckPerms/1243/artifact/bukkit/build/libs/LuckPerms-Bukkit-5.2.77.jar).")
                if "bPermissions" in plugins:
                    embed_var.add_field(name="❌ bPermissions",
                                        value="bPermissions is an outdated permission plugin. "
                                              "Consider replacing it with [LuckPerms](https://ci.lucko.me/job/LuckPerms/1243/artifact/bukkit/build/libs/LuckPerms-Bukkit-5.2.77.jar).")
                if "DisableJoinMessage" in plugins and "Essentials" in plugins:
                    embed_var.add_field(name="❌ DisableJoinMessage",
                                        value="You probably don't need DisableJoinMessage because Essentials already has its features. ")
                for plugin in plugins:
                    if "songoda" in r["timingsMaster"]["plugins"][plugin]["authors"].casefold():
                        if plugin == "EpicHeads":
                            embed_var.add_field(name="❌ EpicHeads",
                                                value="This plugin was made by Songoda. Songoda resources are poorly developed and often cause problems. You should find an alternative such as [HeadsPlus](spigotmc.org/resources/headsplus-»-1-8-1-16-4.40265/) or [HeadDatabase](https://www.spigotmc.org/resources/head-database.14280/).")
                        elif plugin == "UltimateStacker":
                            embed_var.add_field(name="❌ UltimateStacker",
                                                value="Stacking plugins actually cause more lag. "
                                                      "Remove UltimateStacker.")
                        else:
                            embed_var.add_field(name="❌ " + plugin,
                                                value="This plugin was made by Songoda. Songoda resources are poorly developed and often cause problems. You should find an alternative.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                using_purpur = "purpur" in r["timingsMaster"]["config"]
                if using_purpur:
                    plugins = r["timingsMaster"]["plugins"]
                    if "SilkSpawners" in plugins:
                        embed_var.add_field(name="❌ SilkSpawners",
                                            value="You probably don't need SilkSpawners as Purpur already has its features. "
                                                  "Remove SilkSpawners.")
                    if "MineableSpawners" in plugins:
                        embed_var.add_field(name="❌ MineableSpawners",
                                            value="You probably don't need MineableSpawners as Purpur already has its features. "
                                                  "Remove MineableSpawners.")
                    if "VillagerLobotomizatornator" in plugins:
                        embed_var.add_field(name="❌ LimitPillagers",
                                            value="You probably don't need VillagerLobotomizatornator as Purpur already adds its features. "
                                                  "Enable villager.lobotomize.enabled in purpur.yml.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                plugins = r["timingsMaster"]["plugins"]
                if "PhantomSMP" in plugins:
                    phantoms_only_insomniacs = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"][
                        "phantoms-only-attack-insomniacs"]
                    if phantoms_only_insomniacs == "false":
                        embed_var.add_field(name="❌ PhantomSMP",
                                            value="You probably don't need PhantomSMP as Paper already has its features. "
                                                  "Remove PhantomSMP.")
                    else:
                        embed_var.add_field(name="❌ PhantomSMP",
                                            value="You probably don't need PhantomSMP as Paper already has its features. "
                                                  "Enable phantoms-only-attack-insomniacs in paper.yml.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                network_compression_threshold = int(
                    r["timingsMaster"]["config"]["server.properties"]["network-compression-threshold"])
                bungeecord = r["timingsMaster"]["config"]["spigot"]["settings"]["bungeecord"]
                if network_compression_threshold <= 256 and bungeecord == "false":
                    embed_var.add_field(name="❌ network-compression-threshold",
                                        value="Increase this in server.properties. Recommended: 512.")
                if network_compression_threshold != -1 and bungeecord == "true":
                    embed_var.add_field(name="❌ network-compression-threshold",
                                        value="Set this to -1 in server.properties for a bungee server like yours.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                spigot_view_distance = r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["view-distance"]
                view_distance = int(r["timingsMaster"]["config"]["server.properties"]["view-distance"])
                if view_distance >= 10 and spigot_view_distance == "default":
                    embed_var.add_field(name="❌ view-distance",
                                        value="Decrease this from default (10) in spigot.yml. "
                                              "Recommended: 3.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                chunk_gc_period = int(r["timingsMaster"]["config"]["bukkit"]["chunk-gc"]["period-in-ticks"])
                if chunk_gc_period >= 600:
                    embed_var.add_field(name="❌ chunk-gc.period-in-ticks",
                                        value="Decrease this in bukkit.yml.\nRecommended: 400.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                ticks_per_monster_spawns = int(r["timingsMaster"]["config"]["bukkit"]["ticks-per"]["monster-spawns"])
                if ticks_per_monster_spawns == 1:
                    embed_var.add_field(name="❌ ticks-per.monster-spawns",
                                        value="Increase this in bukkit.yml.\nRecommended: 4.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                monsters_spawn_limit = int(r["timingsMaster"]["config"]["bukkit"]["spawn-limits"]["monsters"])
                if monsters_spawn_limit >= 70:
                    embed_var.add_field(name="❌ spawn-limits.monsters",
                                        value="Decrease this in bukkit.yml.\nRecommended: 15.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                water_ambient_spawn_limit = int(r["timingsMaster"]["config"]["bukkit"]["spawn-limits"]["water-ambient"])
                if water_ambient_spawn_limit >= 20:
                    embed_var.add_field(name="❌ spawn-limits.water-ambient",
                                        value="Decrease this in bukkit.yml.\nRecommended: 2.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                ambient_spawn_limit = int(r["timingsMaster"]["config"]["bukkit"]["spawn-limits"]["ambient"])
                if ambient_spawn_limit >= 15:
                    embed_var.add_field(name="❌ spawn-limits.ambient",
                                        value="Decrease this in bukkit.yml.\nRecommended: 1.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                animals_spawn_limit = int(r["timingsMaster"]["config"]["bukkit"]["spawn-limits"]["animals"])
                if animals_spawn_limit >= 10:
                    embed_var.add_field(name="❌ spawn-limits.animals",
                                        value="Decrease this in bukkit.yml.\nRecommended: 3.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                water_animals_spawn_limit = int(r["timingsMaster"]["config"]["bukkit"]["spawn-limits"]["water-animals"])
                if water_animals_spawn_limit >= 15:
                    embed_var.add_field(name="❌ spawn-limits.water-animals",
                                        value="Decrease this in bukkit.yml.\nRecommended: 2.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                mob_spawn_range = int(r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["mob-spawn-range"])
                spigot_view_distance = r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["view-distance"]
                if spigot_view_distance == "default":
                    view_distance = int(r["timingsMaster"]["config"]["server.properties"]["view-distance"])
                    if mob_spawn_range >= 8 and view_distance <= 6:
                        embed_var.add_field(name="❌ mob-spawn-range",
                                            value="Decrease this in spigot.yml. "
                                                  "Recommended: " + str(view_distance - 1) + ".")
                elif mob_spawn_range >= 8 and int(spigot_view_distance) <= 6:
                            embed_var.add_field(name="❌ mob-spawn-range",
                                                value="Decrease this in spigot.yml. "
                                                      "Recommended: " + str(int(spigot_view_distance) - 1) + ".")
            except KeyError:
                unchecked = unchecked + 1

            try:
                animals_entity_activation_range = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "animals"])
                if animals_entity_activation_range >= 32:
                    embed_var.add_field(name="❌ entity-activation-range.animals",
                                        value="Decrease this in spigot.yml. "
                                              "Recommended: 6.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                monsters_entity_activation_range = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "monsters"])
                if monsters_entity_activation_range >= 32:
                    embed_var.add_field(name="❌ entity-activation-range.monsters",
                                        value="Decrease this in spigot.yml. "
                                              "Recommended: 16.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                raiders_entity_activation_range = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "raiders"])
            except KeyError:
                unchecked = unchecked + 1

            try:
                misc_entity_activation_range = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["misc"])
                if misc_entity_activation_range >= 16:
                    embed_var.add_field(name="❌ entity-activation-range.misc",
                                        value="Decrease this in spigot.yml. "
                                              "Recommended: 4.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                water_entity_activation_range = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["water"])
                if water_entity_activation_range >= 16:
                    embed_var.add_field(name="❌ entity-activation-range.water",
                                        value="Decrease this in spigot.yml. "
                                              "Recommended: 12.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                villagers_entity_activation_range = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "villagers"])
                if villagers_entity_activation_range >= 32:
                    embed_var.add_field(name="❌ entity-activation-range.villagers",
                                        value="Decrease this in spigot.yml. "
                                              "Recommended: 16.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                flying_monsters_entity_activation_range = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "flying-monsters"])
            except KeyError:
                unchecked = unchecked + 1

            try:
                tick_inactive_villagers = \
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "tick-inactive-villagers"]
                if tick_inactive_villagers == "true":
                    embed_var.add_field(name="❌ tick-inactive-villagers",
                                        value="Disable this in spigot.yml.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                nerf_spawner_mobs = r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["nerf-spawner-mobs"]
                if nerf_spawner_mobs == "false":
                    embed_var.add_field(name="❌ nerf-spawner-mobs",
                                        value="Enable this in spigot.yml.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                wake_up_inactive_villagers_every = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "wake-up-inactive"]["villagers-every"])
            except KeyError:
                unchecked = unchecked + 1
            try:
                wake_up_inactive_villagers_for = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "wake-up-inactive"]["villagers-every"])
                if wake_up_inactive_villagers_for >= 100:
                    embed_var.add_field(name="❌ wake-up-inactive.villagers-for",
                                        value="Decrease this in spigot.yml. "
                                              "Recommended: 20.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                wake_up_inactive_flying_monsters_for = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "wake-up-inactive"]["villagers-every"])
                if wake_up_inactive_flying_monsters_for >= 100:
                    embed_var.add_field(name="❌ wake-up-inactive.flying-monsters-for",
                                        value="Decrease this in spigot.yml. "
                                              "Recommended: 60.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                wake_up_inactive_animals_every = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "wake-up-inactive"]["villagers-every"])

            except KeyError:
                unchecked = unchecked + 1

            try:
                wake_up_inactive_villagers_max_per_tick = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "wake-up-inactive"]["villagers-every"])
                if wake_up_inactive_villagers_max_per_tick >= 4:
                    embed_var.add_field(name="❌ wake-up-inactive.villagers-max-per-tick",
                                        value="Decrease this in spigot.yml. "
                                              "Recommended: 1.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                wake_up_inactive_animals_for = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "wake-up-inactive"]["villagers-every"])
                if wake_up_inactive_animals_for >= 100:
                    embed_var.add_field(name="❌ wake-up-inactive.animals-for",
                                        value="Decrease this in spigot.yml. "
                                              "Recommended: 40.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                wake_up_inactive_monsters_max_per_tick = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "wake-up-inactive"]["villagers-every"])
                if wake_up_inactive_monsters_max_per_tick >= 8:
                    embed_var.add_field(name="❌ wake-up-inactive.monsters-max-per-tick",
                                        value="Decrease this in spigot.yml. "
                                              "Recommended: 4.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                wake_up_inactive_flying_monsters_max_per_tick = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "wake-up-inactive"]["villagers-every"])
                if wake_up_inactive_flying_monsters_max_per_tick >= 8:
                    embed_var.add_field(name="❌ wake-up-inactive.flying-monsters-max-per-tick",
                                        value="Decrease this in spigot.yml. "
                                              "Recommended: 1.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                wake_up_inactive_flying_monsters_every = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "wake-up-inactive"]["villagers-every"])
            except KeyError:
                unchecked = unchecked + 1

            try:
                wake_up_inactive_monsters_every = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "wake-up-inactive"]["villagers-every"])
            except KeyError:
                unchecked = unchecked + 1

            try:
                wake_up_inactive_animals_max_per_tick = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "wake-up-inactive"]["villagers-every"])
                if wake_up_inactive_animals_max_per_tick >= 4:
                    embed_var.add_field(name="❌ wake-up-inactive.animals-max-per-tick",
                                        value="Decrease this in spigot.yml. "
                                              "Recommended: 2.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                wake_up_inactive_monsters_for = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "wake-up-inactive"]["villagers-every"])
                if wake_up_inactive_monsters_for >= 100:
                    embed_var.add_field(name="❌ wake-up-inactive.monsters-for",
                                        value="Decrease this in spigot.yml. "
                                              "Recommended: 60.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                arrow_despawn_rate = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["arrow-despawn-rate"])
                if arrow_despawn_rate >= 1200:
                    embed_var.add_field(name="❌ arrow-despawn-rate",
                                        value="Decrease this in spigot.yml. "
                                              "Recommended: 300.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                item_merge_radius = float(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["merge-radius"]["item"])
                if item_merge_radius <= 2.5:
                    embed_var.add_field(name="❌ merge-radius.item",
                                        value="Increase this in spigot.yml. "
                                              "Recommended: 4.0.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                exp_merge_radius = float(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["merge-radius"]["exp"])
                if exp_merge_radius <= 3.0:
                    embed_var.add_field(name="❌ merge-radius.exp",
                                        value="Increase this in spigot.yml. "
                                              "Recommended: 6.0.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                max_entity_collisions = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["max-entity-collisions"])
                if max_entity_collisions >= 8:
                    embed_var.add_field(name="❌ max-entity-collisions",
                                        value="Decrease this in spigot.yml. "
                                              "Recommended: 2.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                max_auto_save_chunks_per_tick = int(
                    r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["max-auto-save-chunks-per-tick"])
                if max_auto_save_chunks_per_tick >= 24:
                    embed_var.add_field(name="❌ max-auto-save-chunks-per-tick",
                                        value="Decrease this in paper.yml. "
                                              "Recommended: 6.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                optimize_explosions = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"][
                    "optimize-explosions"]
                if optimize_explosions == "false":
                    embed_var.add_field(name="❌ optimize-explosions",
                                        value="Enable this in paper.yml.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                mob_spawner_tick_rate = int(
                    r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["mob-spawner-tick-rate"])
                if mob_spawner_tick_rate == 1:
                    embed_var.add_field(name="❌ mob-spawner-tick-rate",
                                        value="Increase this in paper.yml. "
                                              "Recommended: 2.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                disable_chest_cat_detection = \
                    r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["game-mechanics"][
                        "disable-chest-cat-detection"]
                if disable_chest_cat_detection == "false":
                    embed_var.add_field(name="❌ disable-chest-cat-detection",
                                        value="Enable this in paper.yml.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                container_update_tick_rate = int(
                    r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["container-update-tick-rate"])
                if container_update_tick_rate == "false":
                    embed_var.add_field(name="❌ container-update-tick-rate",
                                        value="Increase this in paper.yml. "
                                              "Recommended: 3.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                grass_spread_tick_rate = int(
                    r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["grass-spread-tick-rate"])
                if grass_spread_tick_rate == 1:
                    embed_var.add_field(name="❌ grass-spread-tick-rate",
                                        value="Increase this in paper.yml. "
                                              "Recommended: 4")
            except KeyError:
                unchecked = unchecked + 1

            try:
                soft_despawn_range = int(
                    r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["despawn-ranges"]["soft"])
                if soft_despawn_range >= 32:
                    embed_var.add_field(name="❌ despawn-ranges.soft",
                                        value="Decrease this in paper.yml. "
                                              "Recommended: 28")
            except KeyError:
                unchecked = unchecked + 1

            try:
                hard_despawn_range = int(r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["despawn-ranges"]["soft"])
                if hard_despawn_range >= 128:
                    embed_var.add_field(name="❌ despawn-ranges.hard",
                                        value="Decrease this in paper.yml. "
                                              "Recommended: 48")
            except KeyError:
                unchecked = unchecked + 1

            try:
                hopper_disable_move_event = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["hopper"][
                    "disable-move-event"]
                if hopper_disable_move_event == "false":
                    embed_var.add_field(name="❌ hopper.disable-move-event",
                                        value="Enable this in paper.yml.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                non_player_arrow_despawn_rate = int(
                    r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["non-player-arrow-despawn-rate"])
                if non_player_arrow_despawn_rate == -1:
                    embed_var.add_field(name="❌ non-player-arrow-despawn-rate",
                                        value="Set a value in paper.yml. "
                                              "Recommended: 60")
            except KeyError:
                unchecked = unchecked + 1

            try:
                creative_arrow_despawn_rate = int(
                    r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["creative-arrow-despawn-rate"])
                if creative_arrow_despawn_rate == -1:
                    embed_var.add_field(name="❌ creative-arrow-despawn-rate",
                                        value="Set a value in paper.yml. "
                                              "Recommended: 60")
            except KeyError:
                unchecked = unchecked + 1

            try:
                prevent_moving_into_unloaded_chunks = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"][
                    "prevent-moving-into-unloaded-chunks"]
                if prevent_moving_into_unloaded_chunks == "false":
                    embed_var.add_field(name="❌ prevent-moving-into-unloaded-chunks",
                                        value="Enable this in paper.yml.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                eigencraft_redstone = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"][
                    "use-faster-eigencraft-redstone"]
                if eigencraft_redstone == "false":
                    embed_var.add_field(name="❌ use-faster-eigencraft-redstone",
                                        value="Enable this in paper.yml.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                fix_climbing_bypass_gamerule = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["fix-climbing-bypassing-cramming-rule"]
                if fix_climbing_bypass_gamerule == "false":
                    embed_var.add_field(name="❌ fix-climbing-bypassing-cramming-rule",
                                        value="Enable this in paper.yml.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                armor_stands_do_collision_entity_lookups = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["armor-stands-do-collision-entity-lookups"]
                if armor_stands_do_collision_entity_lookups == "true":
                    embed_var.add_field(name="❌ armor-stands-do-collision-entity-lookups",
                                        value="Disable this in paper.yml.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                plugins = r["timingsMaster"]["plugins"]
                armor_stands_tick = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["armor-stands-tick"]
                if armor_stands_tick == "true" and "PetBlocks" not in plugins and "BlockBalls" not in plugins and "ArmorStandTools" not in plugins:
                    embed_var.add_field(name="❌ armor-stands-tick",
                                        value="Disable this in paper.yml.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                per_player_mob_spawns = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"][
                    "per-player-mob-spawns"]
                if per_player_mob_spawns == "false":
                    embed_var.add_field(name="❌ per-player-mob-spawns",
                                        value="Enable this in paper.yml.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                alt_item_despawn_rate_enabled = \
                    r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["alt-item-despawn-rate"]["enabled"]
                if alt_item_despawn_rate_enabled == "false":
                    embed_var.add_field(name="❌ alt-item-despawn-rate.enabled",
                                        value="Enable this in paper.yml.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                no_tick_view_distance = int(
                    r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["viewdistances"][
                        "no-tick-view-distance"])
                if no_tick_view_distance == -1:
                    spigot_view_distance = r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"][
                        "view-distance"]
                    if spigot_view_distance == "default":
                        view_distance = int(r["timingsMaster"]["config"]["server.properties"]["view-distance"])
                        if view_distance >= 4:
                            embed_var.add_field(name="❌ no-tick-view-distance",
                                                value="Set a value in paper.yml. "
                                                      "Recommended: " + str(view_distance) + ". And reduce view-distance in server.properties. Recommended: 3.")
                    elif int(spigot_view_distance) >= 4:
                        embed_var.add_field(name="❌ no-tick-view-distance",
                                            value="Set a value in paper.yml. "
                                                  "Recommended: " + spigot_view_distance + ". And reduce view-distance in spigot.yml. Recommended: 3.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                enable_treasure_maps = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"][
                    "enable-treasure-maps"]
                if enable_treasure_maps == "true":
                    embed_var.add_field(name="❌ enable-treasure-maps",
                                        value="Disable this in paper.yml. Why? Generating treasure maps is extremely expensive and can hang a server if the structure it's trying to locate is really far away.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                projectile_load_save = int(r["timingsMaster"]["config"]["paper"]["world-settings"]["default"][
                                               "projectile-load-save-per-chunk-limit"])
                if projectile_load_save == -1:
                    embed_var.add_field(name="❌ projectile-load-save-per-chunk-limit",
                                        value="Set a value in paper.yml. Recommended: 8.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                use_alternate_keepalive = r["timingsMaster"]["config"]["purpur"]["settings"]["use-alternate-keepalive"]
                plugins = r["timingsMaster"]["plugins"]
                if use_alternate_keepalive == "false" and "TCPShield" not in plugins:
                    embed_var.add_field(name="❌ use-alternate-keepalive",
                                        value="Enable this in purpur.yml.")
                if use_alternate_keepalive == "true" and "TCPShield" in plugins:
                    embed_var.add_field(name="❌ use-alternate-keepalive",
                                        value="Disable this in purpur.yml. It causes issues with TCPShield.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                dont_send_useless_entity_packets = r["timingsMaster"]["config"]["purpur"]["settings"][
                    "dont-send-useless-entity-packets"]
                if dont_send_useless_entity_packets == "false":
                    embed_var.add_field(name="❌ dont-send-useless-entity-packets",
                                        value="Enable this in purpur.yml.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                disable_treasure_searching = \
                    r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["mobs"]["dolphin"][
                        "disable-treasure-searching"]
                if disable_treasure_searching == "false":
                    embed_var.add_field(name="❌ dolphin.disable-treasure-searching",
                                        value="Enable this in purpur.yml.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                brain_ticks = int(
                    r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["mobs"]["villager"][
                        "brain-ticks"])
                if brain_ticks == 1:
                    embed_var.add_field(name="❌ villager.brain-ticks",
                                        value="Increase this in purpur.yml. "
                                              "Recommended: 4.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                iron_golem_radius = int(
                    r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["mobs"]["villager"][
                        "spawn-iron-golem"]["radius"])
                if iron_golem_radius == 0:
                    embed_var.add_field(name="❌ spawn-iron-golem.radius",
                                        value="Set a value in purpur.yml. "
                                              "Recommended: 32.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                iron_golem_limit = int(
                    r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["mobs"]["villager"][
                        "spawn-iron-golem"]["limit"])
                if iron_golem_limit == 0:
                    embed_var.add_field(name="❌ spawn-iron-golem.limit",
                                        value="Set a value in purpur.yml. "
                                              "Recommended: 5.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                aggressive_towards_villager_when_lagging = \
                    r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["mobs"]["zombie"][
                        "aggressive-towards-villager-when-lagging"]
                if aggressive_towards_villager_when_lagging == "true":
                    embed_var.add_field(name="❌ zombie.aggresive-towards-villager-when-lagging",
                                        value="Disable this in purpur.yml.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                entities_can_use_portals = \
                    r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["gameplay-mechanics"][
                        "entities-can-use-portals"]
                if entities_can_use_portals == "true":
                    embed_var.add_field(name="❌ entities-can-use-portals",
                                        value="Disable this in purpur.yml to prevent players from creating chunk anchors.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                lobotomize_enabled = r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["mobs"]["villager"][
                        "lobotomize"]["enabled"]
                if lobotomize_enabled == "false":
                    embed_var.add_field(name="❌ villager.lobotomize.enabled",
                                        value="Enable this in purpur.yml.")
            except KeyError:
                unchecked = unchecked + 1

            try:
                teleport_if_outside_border = r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["gameplay-mechanics"]["player"]["teleport-if-outside-border"]
                if teleport_if_outside_border == "false":
                    embed_var.add_field(name="❌ player.teleport-if-outside-border",
                                        value="Enable this in purpur.yml.")
            except KeyError:
                unchecked = unchecked + 1
        except ValueError:
            embed_var.add_field(name="❌ Invalid Configuration",
                                value="At least one of your configuration files had an invalid data type.")

        if len(embed_var.fields) == 0:
            embed_var.add_field(name="✅ All good",
                                value="Analyzed with no issues")
            await message.reply(embed=embed_var)
            return

        issue_count = len(embed_var.fields)
        if issue_count >= 25:
            embed_var.insert_field_at(index=24, name="Plus " + str(issue_count - 24) + " more recommendations", value="Create a new timings report after resolving some of the above issues to see more.")
        if unchecked > 0:
            embed_var.description = "||" + str(unchecked) + " missing configuration optimizations due to your server version.||"
        await message.reply(embed=embed_var)


def setup(bot):
    bot.add_cog(Timings(bot))
