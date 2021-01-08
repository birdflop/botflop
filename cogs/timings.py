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
        embed_var.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)

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
                network_compression_threshold = int(
                    r["timingsMaster"]["config"]["server.properties"]["network-compression-threshold"])

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
            save_user_cache_on_stop_only = r["timingsMaster"]["config"]["spigot"]["settings"][
                "save-user-cache-on-stop-only"]
            mob_spawn_range = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["mob-spawn-range"])
            spigot_view_distance = r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["view-distance"]
            animals_entity_activation_range = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                    "animals"])
            monsters_entity_activation_range = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                    "monsters"])
            raiders_entity_activation_range = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                    "raiders"])
            misc_entity_activation_range = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["misc"])
            water_entity_activation_range = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"]["water"])
            villagers_entity_activation_range = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                    "villagers"])
            flying_monsters_entity_activation_range = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                    "flying-monsters"])
            tick_inactive_villagers = \
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                    "tick-inactive-villagers"]
            nerf_spawner_mobs = r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["nerf-spawner-mobs"]
            wake_up_inactive_villagers_every = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                    "wake-up-inactive"]["villagers-every"])
            wake_up_inactive_villagers_for = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                    "wake-up-inactive"]["villagers-every"])
            wake_up_inactive_flying_monsters_for = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                    "wake-up-inactive"]["villagers-every"])
            wake_up_inactive_animals_every = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                    "wake-up-inactive"]["villagers-every"])
            wake_up_inactive_villagers_max_per_tick = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                    "wake-up-inactive"]["villagers-every"])
            wake_up_inactive_animals_for = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                    "wake-up-inactive"]["villagers-every"])
            wake_up_inactive_monsters_max_per_tick = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                    "wake-up-inactive"]["villagers-every"])
            wake_up_inactive_flying_monsters_max_per_tick = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                    "wake-up-inactive"]["villagers-every"])
            wake_up_inactive_flying_monsters_every = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                    "wake-up-inactive"]["villagers-every"])
            wake_up_inactive_monsters_every = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                    "wake-up-inactive"]["villagers-every"])
            wake_up_inactive_animals_max_per_tick = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                    "wake-up-inactive"]["villagers-every"])
            wake_up_inactive_monsters_for = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                    "wake-up-inactive"]["villagers-every"])
            arrow_despawn_rate = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["arrow-despawn-rate"])
            item_merge_radius = float(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["merge-radius"]["item"])
            exp_merge_radius = float(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["merge-radius"]["exp"])
            max_entity_collisions = int(
                r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["max-entity-collisions"])

            # paper.yml
            max_auto_save_chunks_per_tick = int(
                r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["max-auto-save-chunks-per-tick"])
            optimize_explosions = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"][
                "optimize-explosions"]
            mob_spawner_tick_rate = int(
                r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["mob-spawner-tick-rate"])
            disable_chest_cat_detection = \
                r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["game-mechanics"][
                    "disable-chest-cat-detection"]
            container_update_tick_rate = int(
                r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["container-update-tick-rate"])
            grass_spread_tick_rate = int(
                r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["grass-spread-tick-rate"])
            soft_despawn_range = int(
                r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["despawn-ranges"]["soft"])
            hard_despawn_range = int(
                r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["despawn-ranges"]["soft"])
            hopper_disable_move_event = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["hopper"][
                "disable-move-event"]
            non_player_arrow_despawn_rate = int(
                r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["non-player-arrow-despawn-rate"])
            creative_arrow_despawn_rate = int(
                r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["creative-arrow-despawn-rate"])
            prevent_moving_into_unloaded_chunks = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"][
                "prevent-moving-into-unloaded-chunks"]
            eigencraft_redstone = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"][
                "use-faster-eigencraft-redstone"]
            armor_stands_tick = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["armor-stands-tick"]
            per_player_mob_spawns = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"][
                "per-player-mob-spawns"]
            alt_item_despawn_rate_enabled = \
                r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["alt-item-despawn-rate"]["enabled"]
            no_tick_view_distance = int(
                r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["viewdistances"][
                    "no-tick-view-distance"])
            phantoms_only_insomniacs = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["phantoms-only-attack-insomniacs"]
            enable_treasure_maps = r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["enable-treasure-maps"]


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
                    embed_var.add_field(name="⚠ Java " + str(j_version),
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
            if "1.8.0_" in jvm_version or jvm_version.startswith("9.") or jvm_version.startswith("10."):
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
            if "VillagerOptimiser" in plugins:
                embed_var.add_field(name="⚠ VillagerOptimiser",
                                    value="You probably don't need VillagerOptimiser as Paper already adds its features. "
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
                if phantoms_only_insomniacs == "false":
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

            if not online_mode and bungeecord == "false":
                embed_var.add_field(name="⚠ online-mode",
                                    value="Enable this in server.properties for security.",
                                    inline=True)
            if network_compression_threshold == 256 and bungeecord == "false":
                embed_var.add_field(name="⚠ network-compression-threshold",
                                    value="Increase this in server.properties. Recommended: 512.",
                                    inline=True)
            if network_compression_threshold != -1 and bungeecord == "true":
                embed_var.add_field(name="⚠ network-compression-threshold",
                                    value="Set this to -1 in server.properties for a bungee server like yours.",
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
            if mob_spawn_range == 8 and view_distance < 7 and spigot_view_distance != "default" and spigot_view_distance < 7:
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
                embed_var.add_field(name="⚠ disable-chest-cat-detection",
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
                                          "Recommended: 48",
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
            if enable_treasure_maps == "true":
                embed_var.add_field(name="⚠ enable-treasure-maps",
                                    value="Disable this in paper.yml. Why? Generating treasure maps is extremely expensive and can hang a server if the structure it's trying to locate is really far away.",
                                    inline=True)

            if "Purpur" in version:
                use_alternate_keepalive = r["timingsMaster"]["config"]["purpur"]["settings"]["use-alternate-keepalive"]
                dont_send_useless_entity_packets = r["timingsMaster"]["config"]["purpur"]["settings"][
                    "dont-send-useless-entity-packets"]
                disable_treasure_searching = \
                    r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["mobs"]["dolphin"][
                        "disable-treasure-searching"]
                brain_ticks = int(
                    r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["mobs"]["villager"][
                        "brain-ticks"])
                iron_golem_radius = int(
                    r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["mobs"]["villager"][
                        "spawn-iron-golem"]["radius"])
                iron_golem_limit = int(
                    r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["mobs"]["villager"][
                        "spawn-iron-golem"]["limit"])
                aggressive_towards_villager_when_lagging = \
                    r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["mobs"]["zombie"][
                        "aggressive-towards-villager-when-lagging"]
                entities_can_use_portals = \
                    r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["gameplay-mechanics"][
                        "entities-can-use-portals"]
                lobotomize_enabled = \
                    r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["mobs"]["villager"][
                        "lobotomize"]["enabled"]
                teleport_if_outside_border = r["timingsMaster"]["config"]["purpur"]["world-settings"]["default"]["gameplay-mechanics"]["player"]["teleport-if-outside-border"]
                projectile_load_save = int(r["timingsMaster"]["config"]["paper"]["world-settings"]["default"]["projectile-load-save-per-chunk-limit"])

                if no_tick_view_distance == -1:
                    if spigot_view_distance == "default":
                        if type(view_distance) == "int" and view_distance >= 4:
                            embed_var.add_field(name="⚠ no-tick-view-distance",
                                                value="Set a value in paper.yml. "
                                                      "Recommended: " + str(
                                                    view_distance) + ". And reduce view-distance in server.properties. Recommended: 3.",
                                                inline=True)
                    else:
                        if int(spigot_view_distance) >= 4:
                            embed_var.add_field(name="⚠ no-tick-view-distance",
                                                value="Set a value in paper.yml. "
                                                      "Recommended: " + spigot_view_distance + ". And reduce view-distance in spigot.yml. Recommended: 3.",
                                                inline=True)
                if use_alternate_keepalive == "false" and "TCPShield" not in plugins:
                    embed_var.add_field(name="⚠ use-alternate-keepalive",
                                        value="Enable this in purpur.yml.",
                                        inline=True)
                if use_alternate_keepalive == "true" and "TCPShield" in plugins:
                    embed_var.add_field(name="⚠ use-alternate-keepalive",
                                        value="Disable this in purpur.yml. It causes issues with TCPShield.",
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
                if teleport_if_outside_border == "false":
                    embed_var.add_field(name="⚠ player.teleport-if-outside-border",
                                        value="Disable this in purpur.yml.",
                                        inline=True)
                if projectile_load_save == -1:
                    embed_var.add_field(name="⚠ projectile-load-save-per-chunk-limit",
                                        value="Set a value in paper.yml. Recommended: 8.",
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
            embed_var.add_field(name="⚠ Outdated Server",
                                value="Please update your server jar.",
                                inline=True)

        await message.channel.send(embed=embed_var)


def setup(bot):
    bot.add_cog(Timings(bot))
