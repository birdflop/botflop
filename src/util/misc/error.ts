import {
  ButtonStyle,
  CommandInteraction,
  ModalSubmitInteraction,
  ButtonInteraction,
  TextChannel,
  Message,
  StringSelectMenuInteraction,
  AttachmentBuilder,
  ContainerBuilder,
  MessageFlags,
} from 'discord.js';
import { readFileSync } from 'fs';
import { logDate } from '~/util/logger';

export async function errorFunc(
  err: any,
  messageOrInteraction:
    | Message
    | CommandInteraction
    | ModalSubmitInteraction
    | ButtonInteraction
    | StringSelectMenuInteraction,
  userError?: boolean
) {
  logger.error(err);

  const client = messageOrInteraction.client;

  // Create error message container
  const ErrorContainer = new ContainerBuilder()
    .setAccentColor(userError ? 0xe7a83c : 0xe74c3c)
    .addSectionComponents((section) =>
      section
        .addTextDisplayComponents((textDisplay) =>
          textDisplay.setContent(
            userError ? '## Invalid command usage' : '## An error has occured!'
          )
        )
        .setButtonAccessory((btn) =>
          btn
            .setStyle(ButtonStyle.Link)
            .setLabel('Support Server')
            .setURL('https://discord.gg/nmgtX5z')
        )
    )
    .addSeparatorComponents((separator) => separator)
    .addTextDisplayComponents((textDisplay) =>
      textDisplay.setContent(`\`\`\`\n${err}\n\`\`\``)
    );

  // log error in support server if it's not a user error
  if (!userError) {
    ErrorContainer.addSeparatorComponents(
      (separator) => separator
    ).addTextDisplayComponents((textDisplay) =>
      textDisplay.setContent(
        'This was most likely an error on our end. Please report this at the Birdflop Discord Server.'
      )
    );
    const channel = client.guilds.cache
      .get('746125698644705524')!
      .channels.cache.get('1257102558074376372') as TextChannel;
    const logFile = new AttachmentBuilder(
      readFileSync(`./logs/${logDate}.log`),
      { name: `${logDate}.log` }
    );
    channel.send({
      files: [logFile],
      components: [ErrorContainer],
      flags: MessageFlags.IsComponentsV2,
    });
  }

  // send error message, if that fails, send it in the channel, if that also fails, log it
  try {
    if (messageOrInteraction instanceof Message) {
      return await messageOrInteraction.reply({
        components: [ErrorContainer],
        flags: MessageFlags.IsComponentsV2,
      });
    } else {
      if (messageOrInteraction.deferred || messageOrInteraction.replied) {
        return await messageOrInteraction.followUp({
          components: [ErrorContainer],
          flags: MessageFlags.IsComponentsV2,
        });
      } else {
        return await messageOrInteraction.reply({
          components: [ErrorContainer],
          flags: MessageFlags.IsComponentsV2,
        });
      }
    }
  } catch (err_1) {
    logger.warn(err_1);
    if (messageOrInteraction.channel && 'send' in messageOrInteraction.channel)
      messageOrInteraction.channel
        .send({
          components: [ErrorContainer],
          flags: MessageFlags.IsComponentsV2,
        })
        .catch((err_2) => logger.warn(err_2));
  }
}
