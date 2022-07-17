const { MessageButton, MessageActionRow, MessageEmbed } = require('discord.js');
module.exports = {
	name: 'ping',
	description: 'Pong!',
	ephemeral: true,
	aliases: ['pong'],
	cooldown: 10,
	async execute(message, args, client) {
		try {
			// Create embed with ping information and add ping again button
			const PingEmbed = new MessageEmbed()
				.setColor(Math.floor(Math.random() * 16777215))
				.setTitle('Pong!')
				.setDescription(`**Message Latency** ${Date.now() - message.createdTimestamp}ms\n**API Latency** ${client.ws.ping}ms`);
			const row = new MessageActionRow()
				.addComponents([
					new MessageButton()
						.setCustomId('ping_again')
						.setLabel('Ping Again')
						.setStyle('SECONDARY'),
				]);

			// reply with embed
			const pingmsg = await message.reply({ embeds: [PingEmbed], components: [row] });

			// create collector for ping again button
			const filter = i => i.customId == 'ping_again';
			const collector = pingmsg.createMessageComponentCollector({ filter, time: args[0] == 'reset' ? 30000 : 120000 });
			collector.on('collect', async interaction => {
				// Check if the button is one of the settings buttons
				interaction.deferUpdate();

				// Set the embed description with new ping stuff
				PingEmbed.setDescription(`**Message Latency** ${Date.now() - interaction.createdTimestamp}ms\n**API Latency** ${client.ws.ping}ms`);

				// Set title and update message
				pingmsg.edit({ embeds: [PingEmbed] });
			});

			// When the collector stops, remove the undo button from it
			collector.on('end', () => pingmsg.edit({ components: [] }));
		}
		catch (err) { client.logger.error(err.stack); }
	},
};