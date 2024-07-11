const analyzeTimings = require('../functions/analyzeTimings.js');
const analyzeProfile = require('../functions/analyzeProfile.js');
const { EmbedBuilder, ApplicationCommandOptionType, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');

module.exports = {
	name: 'analyze',
	description: 'Analyze Paper timings or Spark profiles to help optimize your server.',
	args: true,
	usage: '<Timings/Profiles Link>',
	options: [{
		'type': ApplicationCommandOptionType.String,
		'name': 'url',
		'description': 'The Timings or Profiles URL',
		'required': true,
	}],
	async execute(message, args, client) {
		try {
			const url = args[0];
			let analysisResult;
			let isTimings = false;
			let isProfile = false;

			if (url.includes('timings')) {
				isTimings = true;
				analysisResult = await analyzeTimings(message, client, args);
			}
			else if (url.includes('spark')) {
				isProfile = true;
				analysisResult = await analyzeProfile(message, client, args);
			}

			if (!isTimings && !isProfile) {
				return message.reply('Invalid URL. Please provide a valid Timings or Profile URL.');
			}

			const resultMessage = await message.reply(analysisResult ? analysisResult[0] : 'Invalid URL.');
			if (!analysisResult) return;

			const suggestions = analysisResult[1];
			if (!suggestions) return;

			const filter = i => i.user.id == (message.author ?? message.user).id && i.customId.startsWith('analysis_');
			const collector = resultMessage.createMessageComponentCollector({ filter, time: 300000 });

			collector.on('collect', async i => {
				await i.deferUpdate();

				const AnalysisEmbed = new EmbedBuilder(i.message.embeds[0].toJSON());
				const footer = AnalysisEmbed.toJSON().footer;

				if (i.customId == 'analysis_force') {
					const fields = [...suggestions];
					const components = [];
					if (suggestions.length >= 13) {
						fields.splice(12, suggestions.length, { name: '✅ Your server isn\'t lagging', value: `**Plus ${suggestions.length - 12} more recommendations**\nClick the buttons below to see more` });
						components.push(
							new ActionRowBuilder()
								.addComponents([
									new ButtonBuilder()
										.setCustomId('analysis_prev')
										.setEmoji({ name: '⬅️' })
										.setStyle(ButtonStyle.Secondary),
									new ButtonBuilder()
										.setCustomId('analysis_next')
										.setEmoji({ name: '➡️' })
										.setStyle(ButtonStyle.Secondary),
									new ButtonBuilder()
										.setURL('https://github.com/pemigrade/botflop')
										.setLabel('Botflop')
										.setStyle(ButtonStyle.Link),
								]),
						);
					}
					AnalysisEmbed.setFields(fields);

					return i.editReply({ embeds: [AnalysisEmbed], components });
				}

				const text = footer.text.split(' • ');
				const lastPage = parseInt(text[text.length - 1].split('Page ')[1].split(' ')[0]);
				const maxPages = parseInt(text[text.length - 1].split('Page ')[1].split(' ')[2]);

				const page = i.customId == 'analysis_next' ? lastPage == maxPages ? 1 : lastPage + 1 : lastPage - 1 ? lastPage - 1 : maxPages;
				const end = page * 12;
				const start = end - 12;
				const fields = suggestions.slice(start, end);

				text[text.length - 1] = `Page ${page} of ${Math.ceil(suggestions.length / 12)}`;
				AnalysisEmbed
					.setFields(fields)
					.setFooter({ iconURL: footer.icon_url, text: text.join(' • ') });

				i.editReply({ embeds: [AnalysisEmbed] });
			});

			collector.on('end', () => {
				if (message.commandName) message.editReply({ components: [] }).catch(err => client.logger.warn(err));
				else resultMessage.edit({ components: [] }).catch(err => client.logger.warn(err));
			});
		}
		catch (err) { client.error(err, message); }
	},
};