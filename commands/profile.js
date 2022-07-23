const analyzeProfile = require('../functions/analyzeProfile.js');
const { EmbedBuilder, ApplicationCommandOptionType } = require('discord.js');
module.exports = {
	name: 'profile',
	description: 'Analyze spark profiles to help optimize your server.',
	args: true,
	usage: '<Spark Profile Link>',
	options: [{
		'type': ApplicationCommandOptionType.String,
		'name': 'url',
		'description': 'The Spark Profile URL',
		'required': true,
	}],
	async execute(message, args, client) {
		try {
			const profileresult = await analyzeProfile(message, client, args);
			const profilemsg = await message.reply(profileresult ? profileresult[0] : 'Invalid Profile URL.');
			if (!profileresult) return;

			// Get the issues from the profile result
			const issues = profileresult[1];
			if (issues) {
				const filter = i => i.user.id == (message.author ?? message.user).id && i.customId.startsWith('profile_');
				const collector = profilemsg.createMessageComponentCollector({ filter, time: 300000 });
				collector.on('collect', async i => {
					// Defer button
					i.deferUpdate();

					// Get the embed
					const ProfileEmbed = new EmbedBuilder(i.message.embeds[0].toJSON());
					const footer = ProfileEmbed.toJSON().footer;

					// Calculate total amount of pages and get current page from embed footer
					const text = footer.text.split(' • ');
					const lastPage = parseInt(text[text.length - 1].split('Page ')[1].split(' ')[0]);
					const maxPages = parseInt(text[text.length - 1].split('Page ')[1].split(' ')[2]);

					// Get next page (if last page, go to pg 1)
					const page = i.customId == 'profile_next' ? lastPage == maxPages ? 1 : lastPage + 1 : lastPage - 1 ? lastPage - 1 : maxPages;
					const end = page * 12;
					const start = end - 12;
					const fields = issues.slice(start, end);

					// Update the embed
					text[text.length - 1] = `Page ${page} of ${Math.ceil(issues.length / 12)}`;
					ProfileEmbed
						.setFields(fields)
						.setFooter({ iconURL: footer.icon_url, text: text.join(' • ') });

					// Send the embed
					profilemsg.edit({ embeds: [ProfileEmbed] });
				});
			}
		}
		catch (err) { client.logger.error(err.stack); }
	},
};