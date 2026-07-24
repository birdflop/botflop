import {
  EmbedBuilder,
  Collection,
  Client,
  CommandInteraction,
  TextChannel,
} from 'discord.js';
import checkPerms from '~/util/misc/checkPerms';
import slashcommands, { cooldowns } from '~/lists/cmds';

export default async (
  client: Client<true>,
  interaction: CommandInteraction
) => {
  // Check if interaction is command
  if (!interaction.isChatInputCommand()) return;
  if (interaction.inGuild() && !interaction.inCachedGuild())
    await interaction.guild?.fetch();

  // Get the command from the available slash cmds in the bot, if there isn't one, just return because discord will throw an error itself
  const command = slashcommands.get(interaction.commandName);
  if (!command) return;

  // Get cooldowns and check if cooldown exists, if not, create it
  if (!cooldowns.has(command.name!))
    cooldowns.set(command.name!, new Collection());

  // Get current timestamp and the command's last used timestamps
  const now = Date.now();
  const timestamps = cooldowns.get(command.name!) as Collection<string, number>;

  // Calculate the cooldown in milliseconds (default is 3600 miliseconds, idk why)
  const cooldownAmount = (command.cooldown || 3) * 1200;

  // Check if user is in the last used timestamp
  if (timestamps.has(interaction.user.id)) {
    // Get cooldown expiration timestamp
    const expirationTime =
      timestamps.get(interaction.user.id)! + cooldownAmount;

    // If cooldown expiration hasn't passed, send cooldown message
    if (now < expirationTime) {
      const timeLeft = (expirationTime - now) / 1000;
      const cooldownEmbed = new EmbedBuilder()
        .setColor('Random')
        .setTitle('Cooldown')
        .setDescription(
          `wait ${timeLeft.toFixed(1)} more seconds before reusing the ${command.name} command.`
        );
      return interaction.reply({
        embeds: [cooldownEmbed],
        flags: ['Ephemeral'],
      });
    }
  }

  // Set last used timestamp to now for user and delete the timestamp after cooldown passes
  timestamps.set(interaction.user.id, now);
  setTimeout(() => timestamps.delete(interaction.user.id), cooldownAmount);

  // Log
  logger.info(
    `${interaction.user.username} issued slash command: /${interaction.commandName} ${interaction.options.getSubcommand(false) ?? ''} in ${interaction.guild?.name ?? 'DMs'}`.replace(
      ' ,',
      ','
    )
  );

  // Check if user has the permissions necessary in the channel to use the command
  if (command.channelPermissions && interaction.inCachedGuild()) {
    const permCheck = checkPerms(
      command.channelPermissions,
      interaction.member,
      interaction.channel!
    );
    if (permCheck) return error(permCheck, interaction, true);
  }

  // Check if bot has the permissions necessary in the channel to run the command
  // if it's in dms, we don't need to check for any permissions
  if (command.botChannelPerms && interaction.inCachedGuild()) {
    const permCheck = checkPerms(
      command.botChannelPerms,
      interaction.guild.members.me!,
      interaction.channel!
    );
    if (permCheck) return error(permCheck, interaction, true);
  }

  // Check if bot has the permissions necessary in the guild to run the command
  if (command.botPerms && interaction.inCachedGuild()) {
    const permCheck = checkPerms(
      command.botPerms,
      interaction.guild.members.me!
    );
    if (permCheck) return error(permCheck, interaction, true);
  }

  // Defer and execute the command
  try {
    if (command.defer) await interaction.deferReply({ flags: command.flags });
    command.execute(interaction, client);
  } catch (err) {
    const interactionFailed = new EmbedBuilder()
      .setColor('Random')
      .setTitle('INTERACTION FAILED')
      .setAuthor({
        name: interaction.user.username,
        iconURL: interaction.user.avatarURL() ?? undefined,
      })
      .addFields([
        { name: '**Type:**', value: 'Slash' },
        { name: '**Interaction:**', value: `${command.name}` },
        { name: '**Error:**', value: `\`\`\`\n${err}\n\`\`\`` },
        { name: '**Guild:**', value: interaction.guild?.name ?? 'DMs' },
        { name: '**Channel:**', value: `${interaction.channel}` },
      ]);
    const errorchannel = client.guilds.cache
      .get('811354612547190794')!
      .channels.cache.get('830013224753561630') as TextChannel;
    errorchannel.send({
      content: '<@&839158574138523689>',
      embeds: [interactionFailed],
    });
    interaction.user
      .send({ embeds: [interactionFailed] })
      .catch((err) => logger.warn(err));
    logger.error(err);
  }
};
