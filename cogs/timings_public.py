import discord
from discord.ext import commands
import requests
import yaml
import re

TIMINGS_CHECK = None
YAML_ERROR = None
with open("cogs/timings_check.yml", 'r', encoding="utf8") as stream:
    try:
        TIMINGS_CHECK = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        YAML_ERROR = exc

VERSION_REGEX = re.compile(r"\d+\.\d+\.\d+")


class Timings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.TIMINGS_TITLE = "Timings Analysis"

    async def analyze_timings(self, message):
        words = message.content.replace("\n", " ").split(" ")
        timings_url = ""
        embed_var = discord.Embed(title=self.TIMINGS_TITLE)
        embed_var.set_footer(text="Requested by " + message.author.name + message.author.discriminator, icon_url=message.author.avatar_url)

        for word in words:
            if word.startswith("https://timings.") and "/d=" in word:
                word.replace("/d=", "/?id=")
            if word.startswith("https://timings.") and "/?id=" in word:
                timings_url = word
                embed_var.url = timings_url
                break
            if word.startswith("https://www.spigotmc.org/go/timings?url=") or word.startswith(
                    "https://timings.spigotmc.org/?url="):
                embed_var.add_field(name="❌ Spigot",
                                    value="Spigot timings have limited information. Switch to [Purpur](https://purpur.pl3x.net/downloads) for better timings analysis.")
                embed_var.url = word
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
        timings_url_raw = timings_url + "&raw=1"

        request_raw = requests.get(timings_url_raw).json()
        request = requests.get(timings_json).json()
        if request is None or request_raw is None:
            embed_var.add_field(name="❌ Invalid report",
                                value="Create a new timings report.")
            await message.reply(embed=embed_var)
            return

        try:
            try:
                version = request["timingsMaster"]["version"] if "version" in request["timingsMaster"] else None
                if "version" in TIMINGS_CHECK and version:
                    version_result = VERSION_REGEX.search(version)
                    version_result = version_result.group() if version_result else None
                    if version_result:
                        if compare_versions(version_result, TIMINGS_CHECK["version"]) == -1:
                            version = version.replace("git-", "").replace("MC:", "")
                            embed_var.add_field(name="❌ Legacy Build",
                                                value=f'You are using `{version}`. Update to `{TIMINGS_CHECK["version"]}`')
                    else:
                        embed_var.add_field(name="❗ Value Error",
                                            value=f'Could not locate version from `{version}`')
                if "servers" in TIMINGS_CHECK:
                    for server in TIMINGS_CHECK["servers"]:
                        if server["name"] in version:
                            embed_var.add_field(**create_field(server))
                            break
            except KeyError as key:
                print("Missing: " + str(key))

            try:
                timing_cost = int(request["timingsMaster"]["system"]["timingcost"])
                if timing_cost > 300:
                    embed_var.add_field(name="❌ Timingcost",
                                        value="Your timingcost is " + str(
                                            timing_cost) + ". Find a [better host](https://www.birdflop.com).")
            except KeyError as key:
                print("Missing: " + str(key))

            try:
                jvm_version = request["timingsMaster"]["system"]["jvmversion"]
                if jvm_version.startswith("1.8.") or jvm_version.startswith("9.") or jvm_version.startswith("10."):
                    embed_var.add_field(name="❌ Java Version",
                                        value="You are using Java " + jvm_version + ". Update to [Java 11](https://adoptopenjdk.net/installation.html).")
            except KeyError as key:
                print("Missing: " + str(key))

            try:
                flags = request["timingsMaster"]["system"]["flags"]
                if "-XX:+UseZGC" in flags:
                    jvm_version = request["timingsMaster"]["system"]["jvmversion"]
                    java_version = jvm_version.split(".")[0]
                    if int(java_version) < 14:
                        embed_var.add_field(name="❌ Java " + java_version,
                                            value="If you are going to use ZGC, you should also use Java 14+.")
                elif "-Daikars.new.flags=true" in flags:
                    if "-XX:+PerfDisableSharedMem" not in flags:
                        embed_var.add_field(name="❌ Outdated Flags",
                                            value="Add `-XX:+PerfDisableSharedMem` to flags.")
                    if "XX:G1MixedGCCountTarget=4" not in flags:
                        embed_var.add_field(name="❌ Outdated Flags",
                                            value="Add `-XX:G1MixedGCCountTarget=4` to flags.")
                    if "-XX:+UseG1GC" not in flags:
                        embed_var.add_field(name="❌ Aikar's Flags",
                                            value="You must use G1GC when using Aikar's flags.")
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
            except KeyError as key:
                print("Missing: " + str(key))

            try:
                cpu = int(request["timingsMaster"]["system"]["cpu"])
                if cpu == 1:
                    embed_var.add_field(name="❌ Threads",
                                        value="You have only " + str(
                                            cpu) + " thread. Find a [better host](https://www.birdflop.com).")
                if cpu == 2:
                    embed_var.add_field(name="❌ Threads",
                                        value="You have only " + str(
                                            cpu) + " threads. Find a [better host](https://www.birdflop.com).")
            except KeyError as key:
                print("Missing: " + str(key))

            plugins = request["timingsMaster"]["plugins"] if "plugins" in request["timingsMaster"] else None
            server_properties = request["timingsMaster"]["config"]["server.properties"] if "server.properties" in request["timingsMaster"]["config"] else None
            bukkit = request["timingsMaster"]["config"]["bukkit"] if "bukkit" in request["timingsMaster"]["config"] else None
            spigot = request["timingsMaster"]["config"]["spigot"] if "spigot" in request["timingsMaster"]["config"] else None
            paper = request["timingsMaster"]["config"]["paper"] if "paper" in request["timingsMaster"]["config"] else None
            tuinity = request["timingsMaster"]["config"]["tuinity"] if "tuinity" in request["timingsMaster"]["config"] else None
            purpur = request["timingsMaster"]["config"]["purpur"] if "purpur" in request["timingsMaster"]["config"] else None
            if not YAML_ERROR:
                if "plugins" in TIMINGS_CHECK:
                    for server_name in TIMINGS_CHECK["plugins"]:
                        if server_name in request["timingsMaster"]["config"]:
                            for plugin in plugins:
                                for plugin_name in TIMINGS_CHECK["plugins"][server_name]:
                                    if plugin == plugin_name:
                                        stored_plugin = TIMINGS_CHECK["plugins"][server_name][plugin_name]
                                        if isinstance(stored_plugin, dict):
                                            stored_plugin["name"] = plugin_name
                                            embed_var.add_field(**create_field(stored_plugin))
                                        else:
                                            eval_field(embed_var, stored_plugin, plugin_name, plugins,
                                                       server_properties, bukkit, spigot, paper, tuinity, purpur)
                if "config" in TIMINGS_CHECK:
                    for config_name in TIMINGS_CHECK["config"]:
                        config = TIMINGS_CHECK["config"][config_name]
                        for option_name in config:
                            option = config[option_name]
                            eval_field(embed_var, option, option_name, plugins, server_properties, bukkit,
                                       spigot, paper, tuinity, purpur)
            else:
                embed_var.add_field(name="Error loading YAML file",
                                    value=YAML_ERROR)

            try:
                for plugin in plugins:
                    if "songoda" in request["timingsMaster"]["plugins"][plugin]["authors"].casefold():
                        if plugin == "EpicHeads":
                            embed_var.add_field(name="⚠ EpicHeads",
                                                value="This plugin was made by Songoda. Songoda resources are poorly developed and often cause problems. You should find an alternative such as [HeadsPlus](spigotmc.org/resources/headsplus-»-1-8-1-16-4.40265/) or [HeadDatabase](https://www.spigotmc.org/resources/head-database.14280/).")
                        elif plugin == "UltimateStacker":
                            embed_var.add_field(name="⚠ UltimateStacker",
                                                value="Stacking plugins actually causes more lag. "
                                                      "Remove UltimateStacker.")
                        else:
                            embed_var.add_field(name="⚠ " + plugin,
                                                value="This plugin was made by Songoda. Songoda resources are poorly developed and often cause problems. You should find an alternative.")
            except KeyError as key:
                print("Missing: " + str(key))

            try:
                using_ntvd = True
                worlds = request_raw["worlds"]
                tvd = None
                for world in worlds:
                    tvd = int(request_raw["worlds"][world]["ticking-distance"])
                    ntvd = int(request_raw["worlds"][world]["notick-viewdistance"])
                    if ntvd <= tvd and tvd >= 4:
                        using_ntvd = False
                if not using_ntvd:
                    if spigot["world-settings"]["default"]["view-distance"] == "default":
                        embed_var.add_field(name="❌ no-tick-view-distance",
                                            value="Set in [paper.yml](http://bit.ly/paperconf). Recommended: " + str(
                                                tvd) + ". And reduce view-distance from default (" + str(
                                                tvd) + ") in [spigot.yml](http://bit.ly/spiconf). Recommended: 3.")
                    else:
                        embed_var.add_field(name="❌ no-tick-view-distance",
                                            value="Set in [paper.yml](http://bit.ly/paperconf). Recommended: " + str(
                                                tvd) + ". And reduce view-distance from " + str(
                                                tvd) + " in [spigot.yml](http://bit.ly/spiconf). Recommended: 3.")
            except KeyError as key:
                print("Missing: " + str(key))

            try:
                normal_ticks = request["timingsMaster"]["data"][0]["totalTicks"]
                worst_tps = 20
                index = 0
                while index < len(request["timingsMaster"]["data"]):
                    total_ticks = request["timingsMaster"]["data"][index]["totalTicks"]
                    if total_ticks == normal_ticks:
                        end_time = request["timingsMaster"]["data"][index]["end"]
                        start_time = request["timingsMaster"]["data"][index]["start"]
                        tps = total_ticks / (end_time - start_time)
                        if tps < worst_tps:
                            worst_tps = tps
                    index = index + 1
                if worst_tps < 10:
                    red = 255
                    green = int(255 * (0.1 * worst_tps))
                else:
                    red = int(255 * (-0.1 * worst_tps + 2))
                    green = 255
                color = int(red*256*256 + green*256)
                embed_var.color = color
            except KeyError as key:
                print("Missing: " + str(key))

        except ValueError as value_error:
            print(value_error)
            embed_var.add_field(name="❗ Value Error",
                                value=value_error)

        if len(embed_var.fields) == 0:
            embed_var.add_field(name="✅ All good",
                                value="Analyzed with no issues")
            await message.reply(embed=embed_var)
            return

        issue_count = len(embed_var.fields)
        field_at_index = 24
        if issue_count >= 25:
            embed_var.insert_field_at(index=24, name="Plus " + str(issue_count - 24) + " more recommendations",
                                      value="Create a new timings report after resolving some of the above issues to see more.")
        while len(embed_var) > 6000:
            embed_var.insert_field_at(index=field_at_index,
                                      name="Plus " + str(issue_count - field_at_index) + " more recommendations",
                                      value="Create a new timings report after resolving some of the above issues to see more.")
            del embed_var._fields[(field_at_index + 1):]
            field_at_index -= 1
        await message.reply(embed=embed_var)


def eval_field(embed_var, option, option_name, plugins, server_properties, bukkit, spigot, paper, tuinity, purpur):
    dict_of_vars = {"plugins": plugins, "server_properties": server_properties, "bukkit": bukkit, "spigot": spigot,
                    "paper": paper, "tuinity": tuinity, "purpur": purpur}
    try:
        for option_data in option:
            add_to_field = True
            for expression in option_data["expressions"]:
                for config_name in dict_of_vars:
                    if config_name in expression and not dict_of_vars[config_name]:
                        add_to_field = False
                        break
                if not add_to_field:
                    break
                try:
                    if not eval(expression):
                        add_to_field = False
                        break
                except ValueError as value_error:
                    add_to_field = False
                    print(value_error)
                    embed_var.add_field(name="❗ Value Error",
                                        value=f'`{value_error}`\nexpression:\n`{expression}`\noption:\n`{option_name}`')
            for config_name in dict_of_vars:
                if config_name in option_data["value"] and not dict_of_vars[config_name]:
                    add_to_field = False
                    break
            if add_to_field:
                """ f strings don't like newlines so we replace the newlines with placeholder text before we eval """
                option_data["value"] = eval('f"""' + option_data["value"].replace("\n", "\\|n\\") + '"""').replace(
                    "\\|n\\", "\n")
                embed_var.add_field(**create_field({**{"name": option_name}, **option_data}))
                break

    except KeyError as key:
        print("Missing: " + str(key))


def create_field(option):
    field = {"name": option["name"],
             "value": option["value"]}
    if "prefix" in option:
        field["name"] = option["prefix"] + " " + field["name"]
    if "suffix" in option:
        field["name"] = field["name"] + option["suffix"]
    if "inline" in option:
        field["inline"] = option["inline"]
    return field

# Returns -1 if version A is older than version B
# Returns 0 if version A and B are equivalent
# Returns 1 if version A is newer than version B
def compare_versions(versionA, versionB):
  def normalize(v):
      return [int(x) for x in re.sub(r'(\.0+)*$','', v).split(".")]
  return (normalize(versionA) > normalize(versionB)) - (normalize(versionA) < normalize(versionB))

def setup(bot):
    bot.add_cog(Timings(bot))
