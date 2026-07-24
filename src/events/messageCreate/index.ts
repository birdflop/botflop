import {
  Client,
  Message,
  EmbedBuilder,
  PermissionsBitField,
} from 'discord.js';
import { createPaste } from 'hastebin';
import { analyzeMessageLogs } from '~/util/misc/analyzeLogs';

const FILETYPES = [
  '.log',
  '.txt',
  '.json',
  '.yml',
  '.yaml',
  '.css',
  '.py',
  '.js',
  '.sh',
  '.config',
  '.conf',
];

export default async (_client: Client<true>, message: Message) => {
  if (message.author.bot) return;

  // Check if channel supports sending messages and checking permissions
  if (!('send' in message.channel) || !('permissionsFor' in message.channel)) {
    return;
  }

  // If in guild and bot can't send messages or read history, ignore
  if (message.guild && message.guild.members.me) {
    const permissions = message.channel.permissionsFor(message.guild.members.me);
    if (
      !permissions ||
      !permissions.has(PermissionsBitField.Flags.SendMessages) ||
      !permissions.has(PermissionsBitField.Flags.ReadMessageHistory)
    ) {
      return;
    }
  }

  try {
    // Check attachments for Binflop
    if (message.attachments.size > 0) {
      const firstAttachment = message.attachments.first()!;
      const url = firstAttachment.url;
      const contentType = firstAttachment.contentType ?? '';

      if (!url.endsWith('.html')) {
        const filetypeCategory = contentType.split('/')[0];
        if (
          FILETYPES.some((ext) => url.toLowerCase().endsWith(ext)) ||
          filetypeCategory === 'text'
        ) {
          if ('sendTyping' in message.channel) {
            await message.channel.sendTyping();
          }

          const res = await fetch(url);
          let text = await res.text();

          let truncated = false;
          if (text.length > 100000) {
            text = text.substring(0, 100000);
            truncated = true;
          }

          let response = await createPaste(text, {
            server: 'https://bin.birdflop.com',
          });
          if (truncated) {
            response += '\n(file was truncated because it was too long.)';
          }

          const pasteEmbed = new EmbedBuilder()
            .setTitle('Please use a paste service')
            .setColor(0x1d83d4)
            .setDescription(response)
            .setFooter({
              text: `Requested by ${message.author.tag}`,
              iconURL: message.author.displayAvatarURL(),
            });

          await message.channel.send({ embeds: [pasteEmbed] });
          logger.info(
            `File uploaded by ${message.author.tag} (${message.author.id}): ${response}`
          );
        }
      }
    }

    // Convert pastebin links if present
    const words = message.content.replace(/\n/g, ' ').split(' ');
    for (const word of words) {
      if (word.startsWith('https://pastebin.com/') && word.length === 29) {
        if ('sendTyping' in message.channel) {
          await message.channel.sendTyping();
        }

        const key = word.split('/')[3];
        const res = await fetch(`https://pastebin.com/raw/${key}`);
        let text = await res.text();

        let truncated = false;
        if (text.length > 100000) {
          text = text.substring(0, 100000);
          truncated = true;
        }

        let response = await createPaste(text, {
          server: 'https://bin.birdflop.com',
        });
        if (truncated) {
          response += '\n(file was truncated because it was too long.)';
        }

        const pasteEmbed = new EmbedBuilder()
          .setTitle('Pastebin is blocked in some countries')
          .setColor(0x1d83d4)
          .setDescription(response)
          .setFooter({
            text: `Requested by ${message.author.tag}`,
            iconURL: message.author.displayAvatarURL(),
          });

        await message.channel.send({ embeds: [pasteEmbed] });
        logger.info(
          `Pastebin converted from ${message.author.tag} (${message.author.id}): ${response}`
        );
      }
    }

    // Automatic Timings / Profile analysis on messages
    await analyzeMessageLogs(message, words);
  } catch (err) {
    logger.error(err);
  }
};
