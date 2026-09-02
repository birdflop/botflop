// src/util/logger.ts
import { createLogger, format, transports } from "winston";
var lastStarted = /* @__PURE__ */ new Date();
function minTwoDigits(n) {
  return (n < 10 ? "0" : "") + n;
}
var logDate = `${minTwoDigits(lastStarted.getMonth() + 1)}-${minTwoDigits(lastStarted.getDate())}-${lastStarted.getFullYear()}`;
var logger2 = createLogger({
  format: format.combine(
    format.errors({ stack: true }),
    format.colorize(),
    format.timestamp(),
    format.printf(
      (log) => `[${new Date(log.timestamp).toLocaleString("default", { hour: "numeric", minute: "numeric", second: "numeric", hour12: true })} ${log.level}]: ${log.message}${log.stack ? `
${log.stack}` : ""}`
    )
  ),
  transports: [
    new transports.Console(),
    new transports.File({ filename: `logs/${logDate}.log` })
  ],
  rejectionHandlers: [
    new transports.Console(),
    new transports.File({ filename: `logs/${logDate}.log` })
  ]
});
global.logger = logger2;
logger2.info("Logger started");

// src/index.ts
import { Client as Client10, Partials, GatewayIntentBits } from "discord.js";

// src/util/misc/error.ts
import {
  ButtonStyle,
  Message,
  AttachmentBuilder,
  ContainerBuilder,
  MessageFlags
} from "discord.js";
import { readFileSync } from "fs";
async function errorFunc(err, messageOrInteraction, userError) {
  logger.error(err);
  const client2 = messageOrInteraction.client;
  const ErrorContainer = new ContainerBuilder().setAccentColor(userError ? 15181884 : 15158332).addSectionComponents(
    (section) => section.addTextDisplayComponents(
      (textDisplay) => textDisplay.setContent(
        userError ? "## Invalid command usage" : "## An error has occured!"
      )
    ).setButtonAccessory(
      (btn) => btn.setStyle(ButtonStyle.Link).setLabel("Support Server").setURL("https://discord.gg/nmgtX5z")
    )
  ).addSeparatorComponents((separator) => separator).addTextDisplayComponents(
    (textDisplay) => textDisplay.setContent(`\`\`\`
${err}
\`\`\``)
  );
  if (!userError) {
    ErrorContainer.addSeparatorComponents(
      (separator) => separator
    ).addTextDisplayComponents(
      (textDisplay) => textDisplay.setContent(
        "This was most likely an error on our end. Please report this at the Birdflop Discord Server."
      )
    );
    const channel = client2.guilds.cache.get("746125698644705524").channels.cache.get("1257102558074376372");
    const logFile = new AttachmentBuilder(
      readFileSync(`./logs/${logDate}.log`),
      { name: `${logDate}.log` }
    );
    channel.send({
      files: [logFile],
      components: [ErrorContainer],
      flags: MessageFlags.IsComponentsV2
    });
  }
  try {
    if (messageOrInteraction instanceof Message) {
      return await messageOrInteraction.reply({
        components: [ErrorContainer],
        flags: MessageFlags.IsComponentsV2
      });
    } else {
      if (messageOrInteraction.deferred || messageOrInteraction.replied) {
        return await messageOrInteraction.followUp({
          components: [ErrorContainer],
          flags: MessageFlags.IsComponentsV2
        });
      } else {
        return await messageOrInteraction.reply({
          components: [ErrorContainer],
          flags: MessageFlags.IsComponentsV2
        });
      }
    }
  } catch (err_1) {
    logger.warn(err_1);
    if (messageOrInteraction.channel && "send" in messageOrInteraction.channel)
      messageOrInteraction.channel.send({
        components: [ErrorContainer],
        flags: MessageFlags.IsComponentsV2
      }).catch((err_2) => logger.warn(err_2));
  }
}

// src/util/analytics/mochi.ts
import { MochiClient } from "@mochi-analytics/core";
import { attachMochi } from "@mochi-analytics/discordjs";
import "discord.js";
function setupMochi(client2) {
  const url = process.env.MOCHI_URL;
  const apiKey = process.env.MOCHI_API_KEY;
  if (!url && !apiKey) return;
  if (!url || !apiKey) {
    logger.warn(
      "Mochi analytics disabled: set both MOCHI_URL and MOCHI_API_KEY"
    );
    return;
  }
  const mochi = new MochiClient({
    url,
    apiKey,
    onError: (err) => logger.warn(`Mochi analytics error: ${err.message}`)
  });
  const detachMochi = attachMochi(client2, mochi);
  let shuttingDown = false;
  const shutdown = async () => {
    if (shuttingDown) return;
    shuttingDown = true;
    detachMochi();
    await mochi.shutdown();
  };
  process.once("SIGINT", () => void shutdown().finally(() => process.exit(0)));
  process.once("SIGTERM", () => void shutdown().finally(() => process.exit(0)));
  process.once("beforeExit", () => void shutdown());
  logger.info("Mochi analytics enabled");
}

// src/handlers/error.ts
import "discord.js";
var error_default = (client2) => {
  client2.rest.on(
    "rateLimited",
    (info) => logger.warn(`Encountered ${info.method} rate limit!`)
  );
  process.on("unhandledRejection", (reason) => {
    console.error(reason);
    if (reason.rawError && (reason.rawError.message == "Unknown Message" || reason.rawError.message == "Unknown Interaction" || reason.rawError.message == "Missing Access" || reason.rawError.message == "Missing Permissions")) {
      logger.error(JSON.stringify(reason.requestBody));
    }
  });
  client2.on("disconnect", () => {
    logger.info("Bot is disconnecting...");
  });
  client2.on("reconnecting", () => {
    logger.info("Bot reconnecting...");
  });
  client2.on("warn", (error2) => {
    logger.warn(error2);
  });
  client2.on("error", (error2) => {
    logger.error(error2);
  });
  logger.info("Error Handler Loaded");
};

// src/handlers/event.ts
import "discord.js";

// src/events/clientReady/loadCommands.ts
import {
  ApplicationIntegrationType,
  InteractionContextType as InteractionContextType3,
  SlashCommandBuilder
} from "discord.js";

// src/lists/cmds.ts
import { Collection } from "discord.js";

// src/commands/analyze.ts
import {
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle as ButtonStyle2,
  InteractionContextType,
  MessageFlags as MessageFlags2,
  ContainerBuilder as ContainerBuilder2,
  TextDisplayBuilder
} from "discord.js";
import {
  analyzeProfile,
  analyzeTimings,
  collector as submitCollector
} from "@birdflop/analyze";
var analyze = {
  description: "Analyze Paper timings or Spark profiles to help optimize your server.",
  defer: true,
  cmd: (cmd) => cmd.addStringOption(
    (stringOption) => stringOption.setName("url").setDescription("The Timings or Profiles URL").setRequired(true)
  ).setContexts(InteractionContextType.Guild, InteractionContextType.BotDM),
  async execute(interaction) {
    try {
      const url = interaction.options.getString("url", true);
      let analysisResult;
      let isProfile = false;
      let id;
      if (url.startsWith("https://www.spigotmc.org/go/timings?url=") || url.startsWith("https://spigotmc.org/go/timings?url=")) {
        error(
          "\u274C Spigot timings have limited information. Switch to Purpur (or Paper) for better timings analysis. All your plugins will be compatible, and if you don't like it, you can easily switch back.",
          interaction,
          true
        );
        return;
      } else if (url.startsWith("https://spark.lucko.me")) {
        id = url.replace("https://spark.lucko.me/", "");
        isProfile = true;
      } else if (url.startsWith("https://timin")) {
        id = (url.replace("/d=", "/?id=").replace("timin.gs", "timings.aikar.co").split("#")[0] ?? "").split("\n")[0] ?? "".split("/?id=")[1] ?? "";
      } else {
        error("\u274C This is an invalid link.", interaction, true);
        return;
      }
      if (id.length < 30) {
        analysisResult = await analyzeProfile(id);
        try {
          await submitCollector(
            id,
            "https://api.profiler.birdflop.com",
            "spark"
          );
        } catch (err) {
          console.error("Collector error:", err);
        }
      } else {
        analysisResult = await analyzeTimings(id);
        try {
          await submitCollector(
            id,
            "https://api.profiler.birdflop.com",
            "timings"
          );
        } catch (err) {
          console.error("Collector error:", err);
        }
      }
      if (!analysisResult) {
        error("\u274C Failed to analyze the provided link.", interaction, true);
        return;
      }
      const rawSuggestions = analysisResult;
      const titleText = isProfile ? "## Spark Profile Analysis" : "## Timings Analysis";
      let currentPage = 1;
      const itemsPerPage = 12;
      const totalPages = Math.max(
        1,
        Math.ceil(rawSuggestions.length / itemsPerPage)
      );
      const buildContainer = (page) => {
        const container = new ContainerBuilder2().setAccentColor(5793266);
        container.addTextDisplayComponents(
          (textDisplay) => textDisplay.setContent(
            `${titleText}
These are not magic values. Many of these settings have real consequences on your server's mechanics. See [this guide](https://eternity.community/index.php/paper-optimization/) for detailed information on the functionality of each setting.`
          )
        );
        container.addSeparatorComponents((sep) => sep);
        if (rawSuggestions.length === 0) {
          container.addTextDisplayComponents(
            (td) => td.setContent(
              "\u2705 Your server isn't lagging! No performance recommendations found."
            )
          );
        } else {
          const startIndex = (page - 1) * itemsPerPage;
          const pageSuggestions = rawSuggestions.slice(
            startIndex,
            startIndex + itemsPerPage
          );
          for (const item of pageSuggestions) {
            const content = `**${item.name}**
${item.value}`;
            const textDisplay = new TextDisplayBuilder().setContent(content);
            const firstBtn = item.buttons?.[0];
            if (firstBtn?.url) {
              container.addSectionComponents(
                (section) => section.addTextDisplayComponents(textDisplay).setButtonAccessory(
                  (btn) => btn.setURL(firstBtn.url).setLabel(firstBtn.text || "Link").setStyle(ButtonStyle2.Link)
                )
              );
            } else {
              container.addTextDisplayComponents(textDisplay);
            }
          }
          if (totalPages > 1) {
            container.addSeparatorComponents((sep) => sep);
            container.addTextDisplayComponents(
              (td) => td.setContent(`Page ${page} of ${totalPages}`)
            );
            const actionRow = new ActionRowBuilder().addComponents([
              new ButtonBuilder().setCustomId("analysis_prev").setEmoji({ name: "\u2B05\uFE0F" }).setStyle(ButtonStyle2.Secondary).setDisabled(page === 1),
              new ButtonBuilder().setCustomId("analysis_next").setEmoji({ name: "\u27A1\uFE0F" }).setStyle(ButtonStyle2.Secondary).setDisabled(page === totalPages),
              new ButtonBuilder().setURL("https://github.com/pemigrade/botflop").setLabel("Botflop").setStyle(ButtonStyle2.Link)
            ]);
            container.addActionRowComponents(actionRow);
          }
        }
        return container;
      };
      const initialContainer = buildContainer(currentPage);
      const resultinteraction = await interaction.editReply({
        components: [initialContainer],
        flags: MessageFlags2.IsComponentsV2
      });
      if (totalPages > 1) {
        const filter = (i) => i.user.id === interaction.user.id && i.customId.startsWith("analysis_");
        const btnCollector = resultinteraction.createMessageComponentCollector(
          { filter, time: 3e5 }
        );
        btnCollector.on("collect", async (i) => {
          await i.deferUpdate();
          if (i.customId === "analysis_next") {
            currentPage = currentPage >= totalPages ? 1 : currentPage + 1;
          } else if (i.customId === "analysis_prev") {
            currentPage = currentPage <= 1 ? totalPages : currentPage - 1;
          }
          const updatedContainer = buildContainer(currentPage);
          await i.editReply({
            components: [updatedContainer],
            flags: MessageFlags2.IsComponentsV2
          });
        });
        btnCollector.on("end", () => {
          interaction.editReply({ components: [] }).catch((err) => console.error(err));
        });
      }
    } catch (err) {
      error(err, interaction);
    }
  }
};

// src/commands/ping.ts
import {
  ButtonStyle as ButtonStyle3,
  ContainerBuilder as ContainerBuilder3,
  MessageFlags as MessageFlags3
} from "discord.js";
var ping = {
  description: "Pong!",
  cooldown: 10,
  async execute(interaction, client2) {
    try {
      const PingContainer = new ContainerBuilder3().setAccentColor(5793266).addSectionComponents(
        (section) => section.addTextDisplayComponents(
          (textDisplay) => textDisplay.setContent("# Pong!")
        ).setButtonAccessory(
          (btn) => btn.setCustomId("ping_again").setLabel("Refresh").setStyle(ButtonStyle3.Secondary)
        )
      ).addSeparatorComponents((separator) => separator).addTextDisplayComponents(
        (textDisplay) => textDisplay.setContent(
          `**Message Latency** ${Date.now() - interaction.createdTimestamp}ms
**API Latency** ${client2.ws.ping}ms`
        )
      );
      const pingmsg = await interaction.reply({
        components: [PingContainer],
        flags: MessageFlags3.IsComponentsV2
      });
      const filter = (i) => i.customId == "ping_again";
      const collector = pingmsg.createMessageComponentCollector({
        filter,
        time: 3e4
      });
      collector.on("collect", async (btnint) => {
        await btnint.deferUpdate();
        const DescriptionComponent = PingContainer.components[2];
        DescriptionComponent.setContent(
          `**Message Latency** ${Date.now() - interaction.createdTimestamp}ms
**API Latency** ${client2.ws.ping}ms`
        );
        const TitleSection = PingContainer.components[0];
        const TitleComponent = TitleSection.components[0];
        TitleComponent.setContent("# Pong!");
        await btnint.editReply({ components: [PingContainer] });
      });
      collector.on("end", () => {
        const TitleSection = PingContainer.components[0];
        const TitleComponent = TitleSection.components[0];
        PingContainer.components[0] = TitleComponent;
        interaction.editReply({ components: [PingContainer] });
      });
    } catch (err) {
      error(err, interaction);
    }
  }
};

// src/commands/privacy.ts
import {
  ContainerBuilder as ContainerBuilder4,
  MessageFlags as MessageFlags4
} from "discord.js";
var privacy = {
  description: "View the bot's privacy policy.",
  cooldown: 10,
  async execute(interaction, client2) {
    try {
      const PingContainer = new ContainerBuilder4().setAccentColor(5793266).addSectionComponents(
        (section) => section.addTextDisplayComponents(
          (textDisplay) => textDisplay.setContent("# Privacy Policy")
        )
      ).addSeparatorComponents((separator) => separator).addTextDisplayComponents(
        (textDisplay) => textDisplay.setContent(
          "You can view the bot's privacy policy at https://bin.birdflop.com/apezizinip.txt."
        )
      );
      const pingmsg = await interaction.reply({
        components: [PingContainer],
        flags: MessageFlags4.IsComponentsV2
      });
      const filter = (i) => i.customId == "ping_again";
      const collector = pingmsg.createMessageComponentCollector({
        filter,
        time: 3e4
      });
      collector.on("collect", async (btnint) => {
        await btnint.deferUpdate();
        const DescriptionComponent = PingContainer.components[2];
        DescriptionComponent.setContent(
          `**Message Latency** ${Date.now() - interaction.createdTimestamp}ms
**API Latency** ${client2.ws.ping}ms`
        );
        const TitleSection = PingContainer.components[0];
        const TitleComponent = TitleSection.components[0];
        TitleComponent.setContent("# Pong!");
        await btnint.editReply({ components: [PingContainer] });
      });
      collector.on("end", () => {
        const TitleSection = PingContainer.components[0];
        const TitleComponent = TitleSection.components[0];
        PingContainer.components[0] = TitleComponent;
        interaction.editReply({ components: [PingContainer] });
      });
    } catch (err) {
      error(err, interaction);
    }
  }
};

// src/commands/react.ts
import { InteractionContextType as InteractionContextType2, PermissionsBitField } from "discord.js";
var react = {
  description: "Add a reaction to a message",
  defer: true,
  cmd: (cmd) => cmd.addStringOption(
    (stringOption) => stringOption.setName("id").setDescription("The ID of the message to add the reaction to").setRequired(true)
  ).addStringOption(
    (stringOption) => stringOption.setName("emoji").setDescription("The emoji to react with").setRequired(true)
  ).setDefaultMemberPermissions(PermissionsBitField.Flags.ManageMessages).setContexts(InteractionContextType2.Guild, InteractionContextType2.BotDM),
  flags: ["Ephemeral"],
  botChannelPerms: ["AddReactions"],
  async execute(interaction, client2) {
    try {
      const messageId = interaction.options.getString("id", true);
      const emoji = interaction.options.getString("emoji", true);
      await interaction.channel?.messages.react(messageId, emoji).catch((err) => {
        error(
          `Reaction failed!
\`${err}\`
Use an emote from a server that ${client2.user.username} is in or an emoji.`,
          interaction,
          true
        );
        return;
      });
      interaction.editReply({
        content: `**Added reaction ${emoji} to [this message](${messageId})!**`
      });
    } catch (err) {
      error(err, interaction);
    }
  }
};

// src/lists/cmds.ts
var slashcommands = new Collection();
var cooldowns = new Collection();
var commands = {
  analyze,
  ping,
  privacy,
  react
};
for (const [key, command] of Object.entries(commands)) {
  const name = command.name ?? key;
  if (typeof name === "string") {
    slashcommands.set(name, { ...command, name });
  } else {
    for (const cmdname of name) {
      slashcommands.set(cmdname, {
        ...command,
        name: cmdname,
        description: command.description.replace("{NAME}", cmdname)
      });
    }
  }
}
logger.info(`${slashcommands.size} slash commands loaded`);
var cmds_default = slashcommands;

// src/events/clientReady/loadCommands.ts
var truncateString = (string, maxLength) => string.length > maxLength ? `${string.substring(0, maxLength)}\u2026` : string;
var loadCommands_default = async (client2) => {
  const cmds = [];
  await Promise.all([
    ...cmds_default.map(async (command) => {
      logger.info(`Loading slash command ${command.name}`);
      const cmd = new SlashCommandBuilder().setName(command.name).setDescription(truncateString(command.description, 99)).setContexts(
        InteractionContextType3.Guild,
        InteractionContextType3.BotDM,
        InteractionContextType3.PrivateChannel
      ).setIntegrationTypes(
        ApplicationIntegrationType.GuildInstall,
        ApplicationIntegrationType.UserInstall
      );
      if (command.cmd) command.cmd(cmd);
      cmds.push(cmd);
    })
  ]);
  await client2.application?.commands.set(cmds);
  logger.info(`${cmds.length} slash/context commands loaded`);
};

// src/events/clientReady/status.ts
import { ActivityType } from "discord.js";
var status_default = async (client2) => {
  client2.user.setPresence({
    activities: [{ name: "birdflop.com", type: ActivityType.Custom }],
    status: "online"
  });
};

// src/events/interactionCreate/AutoComplete.ts
import { AutocompleteInteraction } from "discord.js";
var AutoComplete_default = async (client2, interaction) => {
  if (!(interaction instanceof AutocompleteInteraction)) return;
  const command = cmds_default.get(interaction.commandName);
  if (!command || !command.autoComplete) return;
  await command.autoComplete(client2, interaction);
};

// src/events/interactionCreate/Command.ts
import {
  EmbedBuilder,
  Collection as Collection2
} from "discord.js";

// src/util/misc/checkPerms.ts
import {
  PermissionsBitField as PermissionsBitField2
} from "discord.js";
function checkPerms(reqPerms, member, channel) {
  if (member.id == "223585930093658122") return;
  const rejectedPerms = [];
  if (typeof channel == "string")
    channel = member.guild.channels.cache.get(channel);
  let perms = member.permissions;
  if (channel) {
    try {
      perms = member.permissionsIn(channel);
    } catch {
      perms = null;
    }
    if (!perms && channel.parent) {
      try {
        perms = channel.parent ? member.permissionsIn(channel.parent.id) : null;
      } catch {
        perms = null;
      }
    }
    if (!perms) perms = member.permissions;
  }
  reqPerms.forEach((perm) => {
    if (!perms?.has(PermissionsBitField2.Flags[perm])) rejectedPerms.push(perm);
  });
  if (!rejectedPerms.length) return;
  return `${member.displayName} has missing permissions${channel ? ` in #${channel.name}` : ""}: ${rejectedPerms.join(", ")}`;
}

// src/events/interactionCreate/Command.ts
var Command_default = async (client2, interaction) => {
  if (!interaction.isChatInputCommand()) return;
  if (interaction.inGuild() && !interaction.inCachedGuild())
    await interaction.guild?.fetch();
  const command = cmds_default.get(interaction.commandName);
  if (!command) return;
  if (!cooldowns.has(command.name))
    cooldowns.set(command.name, new Collection2());
  const now = Date.now();
  const timestamps = cooldowns.get(command.name);
  const cooldownAmount = (command.cooldown || 3) * 1200;
  if (timestamps.has(interaction.user.id)) {
    const expirationTime = timestamps.get(interaction.user.id) + cooldownAmount;
    if (now < expirationTime) {
      const timeLeft = (expirationTime - now) / 1e3;
      const cooldownEmbed = new EmbedBuilder().setColor("Random").setTitle("Cooldown").setDescription(
        `wait ${timeLeft.toFixed(1)} more seconds before reusing the ${command.name} command.`
      );
      return interaction.reply({
        embeds: [cooldownEmbed],
        flags: ["Ephemeral"]
      });
    }
  }
  timestamps.set(interaction.user.id, now);
  setTimeout(() => timestamps.delete(interaction.user.id), cooldownAmount);
  logger.info(
    `${interaction.user.username} issued slash command: /${interaction.commandName} ${interaction.options.getSubcommand(false) ?? ""} in ${interaction.guild?.name ?? "DMs"}`.replace(
      " ,",
      ","
    )
  );
  if (command.channelPermissions && interaction.inCachedGuild()) {
    const permCheck = checkPerms(
      command.channelPermissions,
      interaction.member,
      interaction.channel
    );
    if (permCheck) return error(permCheck, interaction, true);
  }
  if (command.botChannelPerms && interaction.inCachedGuild()) {
    const permCheck = checkPerms(
      command.botChannelPerms,
      interaction.guild.members.me,
      interaction.channel
    );
    if (permCheck) return error(permCheck, interaction, true);
  }
  if (command.botPerms && interaction.inCachedGuild()) {
    const permCheck = checkPerms(
      command.botPerms,
      interaction.guild.members.me
    );
    if (permCheck) return error(permCheck, interaction, true);
  }
  try {
    if (command.defer) await interaction.deferReply({ flags: command.flags });
    command.execute(interaction, client2);
  } catch (err) {
    const interactionFailed = new EmbedBuilder().setColor("Random").setTitle("INTERACTION FAILED").setAuthor({
      name: interaction.user.username,
      iconURL: interaction.user.avatarURL() ?? void 0
    }).addFields([
      { name: "**Type:**", value: "Slash" },
      { name: "**Interaction:**", value: `${command.name}` },
      { name: "**Error:**", value: `\`\`\`
${err}
\`\`\`` },
      { name: "**Guild:**", value: interaction.guild?.name ?? "DMs" },
      { name: "**Channel:**", value: `${interaction.channel}` }
    ]);
    const errorchannel = client2.guilds.cache.get("811354612547190794").channels.cache.get("830013224753561630");
    errorchannel.send({
      content: "<@&839158574138523689>",
      embeds: [interactionFailed]
    });
    interaction.user.send({ embeds: [interactionFailed] }).catch((err2) => logger.warn(err2));
    logger.error(err);
  }
};

// src/events/messageCreate/index.ts
import { EmbedBuilder as EmbedBuilder2, PermissionsBitField as PermissionsBitField3 } from "discord.js";
import { createPaste } from "hastebin";

// src/util/misc/analyzeLogs.ts
import "discord.js";
import { analyzeProfile as analyzeProfile2, analyzeTimings as analyzeTimings2 } from "@birdflop/analyze";
async function analyzeMessageLogs(message, words) {
  let targetUrl;
  for (const word of words) {
    if (word.startsWith("https://spark.lucko.me/") || word.startsWith("https://timin") || word.startsWith("https://spigotmc.org/go/timings?url=") || word.startsWith("https://www.spigotmc.org/go/timings?url=")) {
      targetUrl = word;
      break;
    }
  }
  if (!targetUrl) return;
  if (targetUrl.startsWith("https://www.spigotmc.org/go/timings?url=") || targetUrl.startsWith("https://spigotmc.org/go/timings?url=")) {
    await message.reply(
      "\u274C Spigot timings have limited information. Switch to Purpur (or Paper) for better timings analysis. All your plugins will be compatible, and if you don't like it, you can easily switch back."
    );
    return;
  }
  let id = "";
  let isProfile = false;
  if (targetUrl.startsWith("https://spark.lucko.me/")) {
    id = targetUrl.replace("https://spark.lucko.me/", "");
    isProfile = true;
  } else if (targetUrl.startsWith("https://timin")) {
    id = (targetUrl.replace("/d=", "/?id=").replace("timin.gs", "timings.aikar.co").split("#")[0] ?? "").split("\n")[0] ?? "";
    if (id.includes("/?id=")) {
      id = id.split("/?id=")[1] ?? "";
    }
  }
  if (!id) return;
  const analysisResult = id.length < 30 ? await analyzeProfile2(id) : await analyzeTimings2(id);
  if (!analysisResult) return;
  const topRecommendations = analysisResult.slice(0, 5);
  let description = isProfile ? "## Spark Profile Analysis Recommendations\n" : "## Timings Analysis Recommendations\n";
  if (topRecommendations.length === 0) {
    description += "\u2705 Your server isn't lagging! No performance recommendations found.";
  } else {
    for (const item of topRecommendations) {
      description += `
**${item.name}**
${item.value}
`;
    }
    if (analysisResult.length > 5) {
      description += `
*Plus ${analysisResult.length - 5} more recommendations. Use \`/analyze\` to view the complete interactive analysis.*`;
    }
  }
  await message.reply({ content: description });
}

// src/events/messageCreate/index.ts
var FILETYPES = [
  ".log",
  ".txt",
  ".json",
  ".yml",
  ".yaml",
  ".css",
  ".py",
  ".js",
  ".sh",
  ".config",
  ".conf"
];
var messageCreate_default = async (_client, message) => {
  if (message.author.bot) return;
  if (!("send" in message.channel) || !("permissionsFor" in message.channel)) {
    return;
  }
  if (message.guild && message.guild.members.me) {
    const permissions = message.channel.permissionsFor(
      message.guild.members.me
    );
    if (!permissions || !permissions.has(PermissionsBitField3.Flags.SendMessages) || !permissions.has(PermissionsBitField3.Flags.ReadMessageHistory)) {
      return;
    }
  }
  try {
    if (message.attachments.size > 0) {
      const firstAttachment = message.attachments.first();
      const url = firstAttachment.url;
      const contentType = firstAttachment.contentType ?? "";
      if (!url.endsWith(".html")) {
        const filetypeCategory = contentType.split("/")[0];
        if (FILETYPES.some((ext) => url.toLowerCase().endsWith(ext)) || filetypeCategory === "text") {
          if ("sendTyping" in message.channel) {
            await message.channel.sendTyping();
          }
          const res = await fetch(url);
          let text = await res.text();
          let truncated = false;
          if (text.length > 1e5) {
            text = text.substring(0, 1e5);
            truncated = true;
          }
          let response = await createPaste(text, {
            server: "https://bin.birdflop.com"
          });
          if (truncated) {
            response += "\n(file was truncated because it was too long.)";
          }
          const pasteEmbed = new EmbedBuilder2().setTitle("Please use a paste service").setColor(1934292).setDescription(response).setFooter({
            text: `Requested by ${message.author.tag}`,
            iconURL: message.author.displayAvatarURL()
          });
          await message.channel.send({ embeds: [pasteEmbed] });
          logger.info(
            `File uploaded by ${message.author.tag} (${message.author.id}): ${response}`
          );
        }
      }
    }
    const words = message.content.replace(/\n/g, " ").split(" ");
    for (const word of words) {
      if (word.startsWith("https://pastebin.com/") && word.length === 29) {
        if ("sendTyping" in message.channel) {
          await message.channel.sendTyping();
        }
        const key = word.split("/")[3];
        const res = await fetch(`https://pastebin.com/raw/${key}`);
        let text = await res.text();
        let truncated = false;
        if (text.length > 1e5) {
          text = text.substring(0, 1e5);
          truncated = true;
        }
        let response = await createPaste(text, {
          server: "https://bin.birdflop.com"
        });
        if (truncated) {
          response += "\n(file was truncated because it was too long.)";
        }
        const pasteEmbed = new EmbedBuilder2().setTitle("Pastebin is blocked in some countries").setColor(1934292).setDescription(response).setFooter({
          text: `Requested by ${message.author.tag}`,
          iconURL: message.author.displayAvatarURL()
        });
        await message.channel.send({ embeds: [pasteEmbed] });
        logger.info(
          `Pastebin converted from ${message.author.tag} (${message.author.id}): ${response}`
        );
      }
    }
    await analyzeMessageLogs(message, words);
  } catch (err) {
    logger.error(err);
  }
};

// src/handlers/event.ts
var event_default = async (client2) => {
  const events = [
    { event: "clientReady", handler: loadCommands_default },
    { event: "clientReady", handler: status_default },
    { event: "interactionCreate", handler: AutoComplete_default },
    { event: "interactionCreate", handler: Command_default },
    { event: "messageCreate", handler: messageCreate_default }
  ];
  for (const { event, handler } of events) {
    client2.on(event, handler.bind(null, client2));
  }
  logger.info(`${events.length} event listeners loaded`);
};

// src/handlers/login.ts
import "discord.js";
var login_default = (client2) => {
  client2.login(process.env.BOT_TOKEN);
  logger.info("Bot logged in");
};

// src/index.ts
import dotenv from "dotenv";
dotenv.config();
var client = new Client10({
  shards: "auto",
  partials: [Partials.Message, Partials.Channel, Partials.User],
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.DirectMessages
  ]
});
global.error = errorFunc;
setupMochi(client);
await error_default(client);
await event_default(client);
await login_default(client);
//# sourceMappingURL=index.js.map