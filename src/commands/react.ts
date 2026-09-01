import { InteractionContextType, PermissionsBitField } from 'discord.js';
import type { Command } from '~/lists/Objects';

export const react: Command<'cached'> = {
  description: 'Add a reaction to a message',
  defer: true,
  cmd: (cmd) =>
    cmd
      .addStringOption((stringOption) =>
        stringOption
          .setName('id')
          .setDescription('The ID of the message to add the reaction to')
          .setRequired(true)
      )
      .addStringOption((stringOption) =>
        stringOption
          .setName('emoji')
          .setDescription('The emoji to react with')
          .setRequired(true)
      )
      .setDefaultMemberPermissions(PermissionsBitField.Flags.ManageMessages)
      .setContexts(InteractionContextType.Guild, InteractionContextType.BotDM),
  flags: ['Ephemeral'],
  botChannelPerms: ['AddReactions'],
  async execute(interaction, client) {
    try {
      const messageId = interaction.options.getString('id', true);

      const emoji = interaction.options.getString('emoji', true);
      await interaction.channel?.messages
        .react(messageId, emoji)
        .catch((err) => {
          error(
            `Reaction failed!\n\`${err}\`\nUse an emote from a server that ${client.user.username} is in or an emoji.`,
            interaction,
            true
          );
          return;
        });

      interaction.editReply({
        content: `**Added reaction ${emoji} to [this message](${messageId})!**`,
      });
    } catch (err) {
      error(err, interaction);
    }
  },
};
