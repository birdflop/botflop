const analyzeTimings = require('../functions/analyzeTimings');
module.exports = {
	name: 'timings_next',
	async execute(interaction, client) {
		// Analyze timings with the url in the author field
		await interaction.editReply(await analyzeTimings(interaction, client, [interaction.message.embeds[0].author.url]));
	},
};