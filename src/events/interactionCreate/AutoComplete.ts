import { AutocompleteInteraction, Client } from 'discord.js';
import slashcommands from '~/lists/cmds';

export default async (
  client: Client<true>,
  interaction: AutocompleteInteraction
) => {
  // Check if the interaction is autocomplete
  if (!(interaction instanceof AutocompleteInteraction)) return;

  // Get the command from the available commands in the bot
  const command = slashcommands.get(interaction.commandName);
  if (!command || !command.autoComplete) return;

  // if autocomplete is set then execute it
  await command.autoComplete(client, interaction);
};
