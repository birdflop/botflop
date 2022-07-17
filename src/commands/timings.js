const analyzeTimings = require('../functions/analyzeTimings.js');
const { EmbedBuilder, ApplicationCommandOptionType } = require('discord.js');
module.exports = {
	name: 'timings',
	description: 'Analyze Paper timings to optimize the Paper server.',
	args: true,
	usage: '<Timings Link>',
	options: [{
		'type': ApplicationCommandOptionType.String,
		'name': 'url',
		'description': 'The Timings URL',
		'required': true,
	}],
	async execute(message, args, client) {
		try {
			const timingsresult = await analyzeTimings(message, client, args);
			const timingsmsg = await message.reply(timingsresult ? timingsresult[0] : 'Invalid Timings URL.');
			if (!timingsresult) return;

			// Get the issues from the timings result
			const issues = timingsresult[1];
			if (issues) {
				const filter = i => i.user.id == message.member.id && i.customId.startsWith('timings_');
				const collector = timingsmsg.createMessageComponentCollector({ filter, time: 300000 });
				collector.on('collect', async i => {
					// Defer button
					i.deferUpdate();

					// Get the embed
					const TimingsEmbed = new EmbedBuilder(i.message.embeds[0].toJSON());
					const footer = TimingsEmbed.toJSON().footer;

					// Calculate total amount of pages and get current page from embed footer
					const text = footer.text.split(' • ');
					const lastPage = parseInt(text[text.length - 1].split('Page ')[1].split(' ')[0]);
					const maxPages = parseInt(text[text.length - 1].split('Page ')[1].split(' ')[2]);

					// Get next page (if last page, go to pg 1)
					const page = i.customId == 'timings_next' ? lastPage == maxPages ? 1 : lastPage + 1 : lastPage - 1 ? lastPage - 1 : maxPages;
					const end = page * 12;
					const start = end - 12;
					const fields = issues.slice(start, end);

					// Update the embed
					text[text.length - 1] = `Page ${page} of ${Math.ceil(issues.length / 12)}`;
					TimingsEmbed
						.setFields(fields)
						.setFooter({ iconURL: footer.iconURL, text: text.join(' • ') });

					// Send the embed
					timingsmsg.edit({ embeds: [TimingsEmbed] });
				});
			}
		}
		catch (err) { client.logger.error(err.stack); }
	},
};