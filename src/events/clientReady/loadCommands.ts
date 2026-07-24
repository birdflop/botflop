import {
  ApplicationIntegrationType,
  Client,
  InteractionContextType,
  SlashCommandBuilder,
  type ApplicationCommandDataResolvable,
} from 'discord.js';
import commands from '~/lists/cmds';

const truncateString = (string: string, maxLength: number) =>
  string.length > maxLength ? `${string.substring(0, maxLength)}…` : string;

export default async (client: Client) => {
  const cmds: ApplicationCommandDataResolvable[] = [];

  await Promise.all([
    ...commands.map(async (command) => {
      logger.info(`Loading slash command ${command.name}`);

      // set name and description from command object
      const cmd = new SlashCommandBuilder()
        .setName(command.name)
        .setDescription(truncateString(command.description, 99))
        .setContexts(
          InteractionContextType.Guild,
          InteractionContextType.BotDM,
          InteractionContextType.PrivateChannel
        )
        .setIntegrationTypes(
          ApplicationIntegrationType.GuildInstall,
          ApplicationIntegrationType.UserInstall
        );

      // Add any options from the command object
      if (command.cmd) command.cmd(cmd);

      cmds.push(cmd);
    }),
  ]);

  await client.application?.commands.set(cmds);
  logger.info(`${cmds.length} slash/context commands loaded`);
};
