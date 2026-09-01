import './util/logger';
import { Client, Partials, GatewayIntentBits } from 'discord.js';
import { errorFunc } from './util/misc/error';
import { setupMochi } from './util/analytics/mochi';
import errorHandler from './handlers/error';
import eventHandler from './handlers/event';
import loginHandler from './handlers/login';
import dotenv from 'dotenv';
dotenv.config();

// Create Discord client
const client = new Client({
  shards: 'auto',
  partials: [Partials.Message, Partials.Channel, Partials.User],
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.DirectMessages,
  ],
});

global.error = errorFunc;
setupMochi(client);

// Load the universal and discord-specific handlers
await errorHandler(client);
await eventHandler(client);
await loginHandler(client);
