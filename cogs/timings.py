import discord
from discord.ext import commands
import requests
import yaml

TIMINGS_CHECK = None
YAML_ERROR = None
with open("cogs/timings_check.yml", 'r') as stream:
    try:
        TIMINGS_CHECK = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        YAML_ERROR = exc

class Timings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.TIMINGS_TITLE = "Timings Analysis"
        self.TIMINGS_TITLE_COLOR = 0x55ffff

    # Use @commands.Cog.listener() instead of event and use @commands.command() for commands

    async def analyze_timings(self, message):
        words = message.content.replace("\n", " ").split(" ")
        timings_url = ""
        embed_var = discord.Embed(title=self.TIMINGS_TITLE, color=self.TIMINGS_TITLE_COLOR)

        for word in words:
            if word.startswith("https://timings.") and "/?id=" in word:
                timings_url = word
                break
            if word.startswith("https://www.spigotmc.org/go/timings?url=") or word.startswith(
                    "https://timings.spigotmc.org/?url="):
                embed_var.add_field(name="❌ Spigot",
                                    value="Upgrade to [Purpur](https://purpur.pl3x.net/downloads/#1.16.4).")
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
            embed_var.add_field(name="❌ Invalid report",
                                value="Create a new timings report.")
            embed_var.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            embed_var.url = timings_url
            await message.reply(embed=embed_var)
            return

        embed_var.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
        embed_var.url = timings_url
        unchecked = 0
        try:
            try:
                version = r["timingsMaster"]["version"].lower()
                if "version" in TIMINGS_CHECK:
                    if TIMINGS_CHECK["version"] in version:
                        embed_var.add_field(name="❌ Legacy Build",
                                            value="Update to " + TIMINGS_CHECK["server"]["version"])
                if "servers" in TIMINGS_CHECK:
                    for server in TIMINGS_CHECK["servers"]:
                        if server["name"] in version:
                            embed_var.add_field(**create_field(server))
                            break
            except KeyError:
                unchecked = unchecked + 1

            try:
                if "config" in TIMINGS_CHECK:
                    server_properties = None
                    bukkit = None
                    spigot = None
                    paper = None
                    purpur = None
                    if "server.properties" in r["timingsMaster"]["config"]:
                        server_properties = r["timingsMaster"]["config"]["server.properties"]
                    if "bukkit" in r["timingsMaster"]["config"]:
                        bukkit = r["timingsMaster"]["config"]["bukkit"]
                    if "spigot" in r["timingsMaster"]["config"]:
                        spigot = r["timingsMaster"]["config"]["spigot"]
                    if "paper" in r["timingsMaster"]["config"]:
                        paper = r["timingsMaster"]["config"]["paper"]
                    if "purpur" in r["timingsMaster"]["config"]:
                        purpur = r["timingsMaster"]["config"]["purpur"]

                    for config_name in TIMINGS_CHECK["config"]:
                        config = TIMINGS_CHECK["config"][config_name]
                        for option_name in config:
                            option = config[option_name]
                            for expression in option["expressions"]:
                                if not eval(expression):
                                    continue
                                embed_var.add_field(**create_field({**{"name": option_name}, **option}))

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
                if not YAML_ERROR:
                    for server_name in TIMINGS_CHECK["plugins"]:
                        if server_name in r["timingsMaster"]["config"]:
                            for plugin in plugins:
                                for plugin_name in TIMINGS_CHECK["plugins"][server_name]:
                                    if plugin == plugin_name:
                                        stored_plugin = TIMINGS_CHECK["plugins"][server_name][plugin_name]
                                        stored_plugin["name"] = plugin_name
                                        embed_var.add_field(**create_field(stored_plugin))
                else:
                    embed_var.add_field(name="Error loading YAML file",
                                        value=YAML_ERROR)
                for plugin in plugins:
                    if "songoda" in r["timingsMaster"]["plugins"][plugin]["authors"].casefold():
                        if plugin == "EpicHeads":
                            embed_var.add_field(name="❌ EpicHeads",
                                                value="This plugin was made by Songoda. Songoda resources are poorly developed and often cause problems. You should find an alternative such as [HeadsPlus](spigotmc.org/resources/headsplus-»-1-8-1-16-4.40265/) or [HeadDatabase](https://www.spigotmc.org/resources/head-database.14280/).")
                        elif plugin == "UltimateStacker":
                            embed_var.add_field(name="❌ UltimateStacker",
                                                value="Stacking plugins actually causes more lag. "
                                                      "Remove UltimateStacker.")
                        else:
                            embed_var.add_field(name="❌ " + plugin,
                                                value="This plugin was made by Songoda. Songoda resources are poorly developed and often cause problems. You should find an alternative.")
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
                raiders_entity_activation_range = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "raiders"])
            except KeyError:
                unchecked = unchecked + 1

            try:
                flying_monsters_entity_activation_range = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "flying-monsters"])
            except KeyError:
                unchecked = unchecked + 1

            try:
                wake_up_inactive_villagers_every = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "wake-up-inactive"]["villagers-every"])
            except KeyError:
                unchecked = unchecked + 1


            try:
                wake_up_inactive_animals_every = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "wake-up-inactive"]["animals-every"])

            except KeyError:
                unchecked = unchecked + 1



            try:
                wake_up_inactive_flying_monsters_every = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "wake-up-inactive"]["flying-monsters-every"])
            except KeyError:
                unchecked = unchecked + 1

            try:
                wake_up_inactive_monsters_every = int(
                    r["timingsMaster"]["config"]["spigot"]["world-settings"]["default"]["entity-activation-range"][
                        "wake-up-inactive"]["monsters-every"])
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

def create_field(option):
    field = {"name": option["name"],
            "value": option["value"]}
    if "prefix" in option:
        field["name"] = option["prefix"] + field["name"]
    if "suffix" in option:
        field["name"] = field["name"] + option["suffix"]
    if "inline" in option:
        field["inline"] = option["inline"]
    return field

def setup(bot):
    bot.add_cog(Timings(bot))
