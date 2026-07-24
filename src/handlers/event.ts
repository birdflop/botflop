import { Client } from 'discord.js';
import { readdirSync } from 'fs';
import { srcDir } from '..';

export default async (client: Client) => {
  const eventFolders = readdirSync(`${srcDir}/events/`);
  let listeners = 0;
  await Promise.all(
    eventFolders.map(async (event) => {
      const jsFiles = readdirSync(`${srcDir}/events/${event}`).filter(
        (subfile) => subfile.endsWith('.js') || subfile.endsWith('.ts')
      );
      await Promise.all(
        jsFiles.map(async (file) => {
          const module = await import(`../events/${event}/${file}`);

          const js = module.default ?? module;
          client.on(event, js.bind(null, client));
        })
      );
      listeners += jsFiles.length;
    })
  );
  logger.info(`${listeners} event listeners loaded`);
};
