import '~/util/logger';
import { Collection } from 'discord.js';
import type { LoadedCommand, Command } from '~/lists/Objects';
import { analyze } from '../commands/analyze';
import { ping } from '../commands/ping';
import { privacy } from '../commands/privacy';
import { react } from '../commands/react';

// Set the slash commands collection
const slashcommands = new Collection<string, LoadedCommand>();
const cooldowns = new Collection<string, Collection<string, number>>();

const commands: Record<string, Command<any>> = {
  analyze,
  ping,
  privacy,
  react,
};

for (const [key, command] of Object.entries(commands)) {
  const name = command.name ?? key;
  if (typeof name === 'string') {
    slashcommands.set(name, { ...command, name });
  } else {
    for (const cmdname of name) {
      slashcommands.set(cmdname, {
        ...command,
        name: cmdname,
        description: command.description.replace('{NAME}', cmdname),
      });
    }
  }
}

logger.info(`${slashcommands.size} slash commands loaded`);

export default slashcommands;
export { cooldowns };
