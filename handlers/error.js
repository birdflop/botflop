const { EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');

module.exports = client => {
	// Create a function for error messaging
	client.error = function error(err, message, userError) {
		if (`${err}`.includes('Received one or more errors')) console.log(err);
		err = err.stack ?? err;
		client.logger.error(err);
		const errEmbed = new EmbedBuilder()
			.setColor(0xE74C3C)
			.setTitle('An error has occured!')
			.setDescription(`\`\`\`\n${err}\n\`\`\``);
		const row = [];
		if (!userError) {
			errEmbed.setFooter({ text: 'This was most likely an error on our end. Please report this at the Birdflop Discord' });
			row.push(new ActionRowBuilder()
				.addComponents([
					new ButtonBuilder()
						.setURL('https://discord.gg/nmgtX5z')
						.setLabel('Birdflop')
						.setStyle(ButtonStyle.Link),
				]));
		}
		message.reply({ embeds: [errEmbed], components: row }).catch(err => {
			client.logger.warn(err);
			message.channel.send({ embeds: [errEmbed], components: row }).catch(err => client.logger.warn(err));
		});
	};
	client.rest.on('rateLimited', (info) => client.logger.warn(`Encountered ${info.method} rate limit!`));
	process.on('unhandledRejection', (reason) => {
		if (reason.rawError && (reason.rawError.message == 'Unknown Message' || reason.rawError.message == 'Unknown Interaction' || reason.rawError.message == 'Missing Access' || reason.rawError.message == 'Missing Permissions')) {
			client.logger.error(JSON.stringify(reason.requestBody));
		}
	});
	client.logger.info('Error Handler Loaded');
};