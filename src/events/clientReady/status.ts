import { ActivityType, Client } from 'discord.js';

export default async (client: Client<true>) => {
  client.user.setPresence({
    activities: [{ name: 'birdflop.com', type: ActivityType.Custom }],
    status: 'online',
  });
};
