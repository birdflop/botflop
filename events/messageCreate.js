const analyzeTimings = require('../functions/analyzeTimings');
const { EmbedBuilder } = require('discord.js');
module.exports = async (client, message) => {
	if (message.author.bot) return;
	const timingsresult = await analyzeTimings(message, client, message.content.split(' '));
	if (!timingsresult) return;
	const timingsmsg = await message.reply(timingsresult[0]);

	// Get the issues from the timings result
	const issues = timingsresult[1];
	if (issues) {
		const filter = i => i.user.id == message.member.id && i.customId.startsWith('timings_');
		const collector = timingsmsg.createMessageComponentCollector({ filter, time: 300000 });
		collector.on('collect', async i => {
			// Defer button
			i.deferUpdate();

			// Get the embed and clear the fields
			const TimingsEmbed = new EmbedBuilder(timingsmsg.embeds[0].toJSON());
			TimingsEmbed.setFields(...issues);

			// Get page from footer
			const footer = TimingsEmbed.toJSON().footer.text.split(' • ');
			let page = parseInt(footer[footer.length - 1].split('Page ')[1].split(' ')[0]);

			// Add/Remove page depending on the customId
			if (i.customId == 'timings_next') page = page + 1;
			if (i.customId == 'timings_prev') page = page - 1;

			// Turn to last page if page is 0 and turn to first page if page is more than the max page
			if (page == 0) page = Math.ceil(issues.length / 12);
			if (page > Math.ceil(issues.length / 12)) page = 1;

			// idk what happened here but it works
			const index = page * 12;
			TimingsEmbed.toJSON().fields.splice(0, index - 12);
			TimingsEmbed.toJSON().fields.splice(index, issues.length);
			footer[footer.length - 1] = `Page ${page} of ${Math.ceil(issues.length / 12)}`;
			TimingsEmbed.setFooter({ text: footer.join(' • ') });

			// Send the embed
			timingsmsg.edit({ embeds: [TimingsEmbed] });
		});
	}
};