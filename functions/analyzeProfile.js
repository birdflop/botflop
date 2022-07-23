const { EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');
const YAML = require('yaml');
const fs = require('fs');
const createField = require('./createField.js');
const evalField = require('./evalField.js');
const Pbf = require('pbf');
const { HeapData, SamplerData } = require('../analysis_config/profile/protos');

// Function to parse the data payload from a request given the schema type
function parse(buf, schema) {
	const pbf = new Pbf(new Uint8Array(buf));
	return schema.read(pbf);
}

module.exports = async function analyzeProfile(message, client, args) {
	const author = message.author ?? message.user;
	const ProfileEmbed = new EmbedBuilder()
		.setDescription('These are not magic values. Many of these settings have real consequences on your server\'s mechanics. See [this guide](https://eternity.community/index.php/paper-optimization/) for detailed information on the functionality of each setting.')
		.setFooter({ text: `Requested by ${author.tag}`, iconURL: author.avatarURL() });

	let url;
	const fields = [];

	args.forEach(arg => {
		if (message.commandName && (arg.startsWith('https://timin') || arg.startsWith('https://www.spigotmc.org/go/timings?url=') || arg.startsWith('https://spigotmc.org/go/timings?url='))) {
			ProfileEmbed.addFields([{ name: '⚠️ Timings Report', value: 'This is a Timings report. Use /timings instead for this type of report.' }]);
			return [{ embeds: [ProfileEmbed] }];
		}
		if (arg.startsWith('https://spark.lucko.me/')) url = arg;
	});

	if (!url) return false;

	// Start typing
	if (!message.commandName) await message.channel.sendTyping();

	client.logger.info(`Spark Profile analyzed from ${author.tag} (${author.id}): ${url}`);

	let error;
	const code = url.replace('https://spark.lucko.me/', '');
	const bytebin = `https://bytebin.lucko.me/${code}`;
	let sampler;
	try {
		const req = await fetch(bytebin);
		const buf = await req.arrayBuffer();
		sampler = parse(buf, SamplerData);
	}
	catch (err) {
		error = err;
	}

	ProfileEmbed.setAuthor({ name: 'Spark Profile Analysis', iconURL: 'https://i.imgur.com/deE1oID.png', url: url });

	if (error) {
		ProfileEmbed.addFields([
			{ name: '❌ Invalid Profile', value: 'Create a new Spark Profile.' },
			{ name: '❌ Error', value: `\`\`\`\n${error}\n\`\`\`` },
		]);
		return [{ embeds: [ProfileEmbed] }];
	}

	let version = sampler.metadata.platform.version;
	client.logger.info(version);

	if (version.endsWith('(MC: 1.17)')) version = version.replace('(MC: 1.17)', '(MC: 1.17.0)');

	let server_properties, bukkit, spigot, paper, purpur;

	const configs = sampler.metadata.serverConfigurations;
	if (configs) {
		if (configs['server.properties']) server_properties = JSON.parse(configs['server.properties']);
		if (configs['bukkit.yml']) bukkit = JSON.parse(configs['bukkit.yml']);
		if (configs['spigot.yml']) spigot = JSON.parse(configs['spigot.yml']);
		if (configs['paper/']) paper = JSON.parse(configs['paper/']);
		if (configs['purpur.yml']) purpur = JSON.parse(configs['purpur.yml']);
	}

	const PROFILE_CHECK = {
		servers: await YAML.parse(fs.readFileSync('./analysis_config/servers.yml', 'utf8')),
		config: {
			'server.properties': await YAML.parse(fs.readFileSync('./analysis_config/server.properties.yml', 'utf8')),
			bukkit: await YAML.parse(fs.readFileSync('./analysis_config/bukkit.yml', 'utf8')),
			spigot: await YAML.parse(fs.readFileSync('./analysis_config/spigot.yml', 'utf8')),
			paper: await YAML.parse(fs.readFileSync('./analysis_config/profile/config/paper.yml', 'utf8')),
			purpur: await YAML.parse(fs.readFileSync('./analysis_config/purpur.yml', 'utf8')),
		},
	};

	console.log(configs);
};