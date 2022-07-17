const { ActionRowBuilder, EmbedBuilder, ButtonBuilder, ButtonStyle, ComponentType } = require('discord.js');
module.exports = {
	name: 'ping',
	description: 'Pong!',
	ephemeral: true,
	aliases: ['pong'],
	cooldown: 10,
	async execute(message, args, client) {
		try {
			// Create embed with ping information and add ping again button
			const PingEmbed = new EmbedBuilder()
				.setColor("Random")
				.setTitle('Pong!')
				.setDescription(`**Message Latency** ${Date.now() - message.createdTimestamp}ms\n**API Latency** ${client.ws.ping}ms`);

			// reply with embed
			const pingmsg = await message.reply({ embeds: [PingEmbed] });
		}
		catch (err) { client.logger.error(err.stack); }
	},
};