const { MessageEmbed, MessageActionRow, MessageButton } = require('discord.js');
const fetch = (...args) => import('node-fetch').then(({ default: e }) => e(...args));
const YAML = require('yaml');
const fs = require('fs');
const createField = require('./createField.js');
const evalField = require('./evalField.js');

module.exports = async function analyzeTimings(message, client, args) {
	const TimingsEmbed = new MessageEmbed()
		.setDescription('These are not magic values. Many of these settings have real consequences on your server\'s mechanics. See [this guide](https://eternity.community/index.php/paper-optimization/) for detailed information on the functionality of each setting.')
		.setFooter({ text: `Requested by ${(message.author ?? message.member.user).tag}`, iconURL: (message.author ?? message.member.user).avatarURL() });

	let url;
	const fields = [];

	args.forEach(arg => {
		if (arg.startsWith('https://timin') && arg.includes('?id=')) url = arg.replace('/d=', '/?id=').replace('timin.gs', 'timings.aikar.co').split('#')[0].split('\n')[0];
		if (arg.startsWith('https://www.spigotmc.org/go/timings?url=') || arg.startsWith('https://spigotmc.org/go/timings?url=')) {
			TimingsEmbed.addFields([{ name: '❌ Spigot', value: 'Spigot timings have limited information. Switch to [Purpur](https://purpurmc.org) for better timings analysis. All your plugins will be compatible, and if you don\'t like it, you can easily switch back.' }])
				.setURL(url);
			return [{ embeds: [TimingsEmbed] }];
		}
	});

	if (!url) return false;

	// Start typing
	await message.channel.sendTyping();

	client.logger.info(`Timings analyzed from ${(message.author ?? message.member.user).tag} (${(message.author ?? message.member.user).id}): ${url}`);

	const timings_host = url.split('?id=')[0];
	const timings_id = url.split('?id=')[1];

	const timings_json = timings_host + 'data.php?id=' + timings_id;
	const url_raw = url + '&raw=1';

	const response_raw = await fetch(url_raw);
	const request_raw = await response_raw.json();
	const response_json = await fetch(timings_json);
	const request = await response_json.json();

	if (request_raw == null) {
		TimingsEmbed.fields = ({
			name: '❌ Processing Error',
			value: 'The bot cannot process this timings report. Please use an alternative timings report.',
			inline: true,
		});
		TimingsEmbed.setColor(parseInt('0xff0000'));
		TimingsEmbed.setDescription('');
		return [{ embeds: [TimingsEmbed] }];
	}

	const server_icon = timings_host + 'image.php?id=' + request_raw.icon;
	TimingsEmbed.setAuthor({ name: 'Timings Analysis', iconURL: (server_icon ?? 'https://i.imgur.com/deE1oID.png'), url: url });

	if (!request_raw || !request) {
		TimingsEmbed.addFields([{ name: '❌ Invalid report', value: 'Create a new timings report.', inline: true }]);
		return [{ embeds: [TimingsEmbed] }];
	}

	let version = request.timingsMaster.version;
	client.logger.info(version);

	if (version.endsWith('(MC: 1.17)')) version = version.replace('(MC: 1.17)', '(MC: 1.17.0)');

	const plugins = Object.keys(request.timingsMaster.plugins).map(i => { return request.timingsMaster.plugins[i]; });
	const server_properties = request.timingsMaster.config ? request.timingsMaster.config['server.properties'] : null;
	const bukkit = request.timingsMaster.config ? request.timingsMaster.config.bukkit : null;
	const spigot = request.timingsMaster.config ? request.timingsMaster.config.spigot : null;
	const paper = request.timingsMaster.config ? (request.timingsMaster.config.paper ?? request.timingsMaster.config.paperspigot) : null;
	const pufferfish = request.timingsMaster.config ? request.timingsMaster.config.pufferfish : null;
	const purpur = request.timingsMaster.config ? request.timingsMaster.config.purpur : null;

	const TIMINGS_CHECK = {
		servers: await YAML.parse(fs.readFileSync('./timings_config/servers.yml', 'utf8')),
		plugins: {
			paper: await YAML.parse(fs.readFileSync('./timings_config/plugins/paper.yml', 'utf8')),
			purpur: await YAML.parse(fs.readFileSync('./timings_config/plugins/purpur.yml', 'utf8')),
		},
		config: {
			'server.properties': await YAML.parse(fs.readFileSync('./timings_config/config/server.properties.yml', 'utf8')),
			bukkit: await YAML.parse(fs.readFileSync('./timings_config/config/bukkit.yml', 'utf8')),
			spigot: await YAML.parse(fs.readFileSync('./timings_config/config/spigot.yml', 'utf8')),
			paper: await YAML.parse(fs.readFileSync(`./timings_config/config/paper-v${paper._version ? 28 : 27}.yml`, 'utf8')),
			pufferfish: await YAML.parse(fs.readFileSync('./timings_config/config/pufferfish.yml', 'utf8')),
			purpur: await YAML.parse(fs.readFileSync('./timings_config/config/purpur.yml', 'utf8')),
		},
	};

	const timing_cost = parseInt(request.timingsMaster.system.timingcost);
	if (timing_cost > 300) {
		fields.push({ name: '❌ Timingcost', value: `Your timingcost is ${timing_cost}. Your cpu is overloaded and/or slow. Find a [better host](https://www.birdflop.com).`, inline: true });
	}

	// fetch the latest mc version
	const req = await fetch('https://api.purpurmc.org/v2/purpur');
	const json = await req.json();
	const latest = json.versions[json.versions.length - 1];

	// ghetto version check
	if (version.split('(MC: ')[1].split(')')[0] != latest) {
		version = version.replace('git-', '').replace('MC: ', '');
		fields.push({ name: '❌ Outdated', value: `You are using \`${version}\`. Update to \`${latest}\`.`, inline: true });
	}

	if (TIMINGS_CHECK.servers) {
		TIMINGS_CHECK.servers.forEach(server => {
			if (version.includes(server.name)) fields.push(createField(server));
		});
	}

	const flags = request.timingsMaster.system.flags;
	const jvm_version = request.timingsMaster.system.jvmversion;
	if (flags.includes('-XX:+UseZGC') && flags.includes('-Xmx')) {
		const flaglist = flags.split(' ');
		flaglist.forEach(flag => {
			if (flag.startsWith('-Xmx')) {
				let max_mem = flag.split('-Xmx')[1];
				max_mem = max_mem.replace('G', '000');
				max_mem = max_mem.replace('M', '');
				max_mem = max_mem.replace('g', '000');
				max_mem = max_mem.replace('m', '');
				if (parseInt(max_mem) < 10000) fields.push({ name: '❌ Low Memory', value:'ZGC is only good with a lot of memory.', inline: true });
			}
		});
	}
	else if (flags.includes('-Daikars.new.flags=true')) {
		if (!flags.includes('-XX:+PerfDisableSharedMem')) fields.push({ name: '❌ Outdated Flags', value: 'Add `-XX:+PerfDisableSharedMem` to flags.', inline: true });
		if (!flags.includes('-XX:G1MixedGCCountTarget=4')) fields.push({ name: '❌ Outdated Flags', value: 'Add `XX:G1MixedGCCountTarget=4` to flags.', inline: true });
		if (!flags.includes('-XX:+UseG1GC') && jvm_version.startsWith('1.8.')) fields.push({ name: '❌ Aikar\'s Flags', value: 'You must use G1GC when using Aikar\'s flags.', inline: true });
		if (flags.includes('-Xmx')) {
			let max_mem = 0;
			const flaglist = flags.split(' ');
			flaglist.forEach(flag => {
				if (flag.startsWith('-Xmx')) {
					max_mem = flag.split('-Xmx')[1];
					max_mem = max_mem.replace('G', '000');
					max_mem = max_mem.replace('M', '');
					max_mem = max_mem.replace('g', '000');
					max_mem = max_mem.replace('m', '');
				}
			});
			if (parseInt(max_mem) < 5400) fields.push({ name: '❌ Low Memory', value: 'Allocate at least 6-10GB of ram to your server if you can afford it.', inline: true });
			let index = 0;
			let max_online_players = 0;
			while (index < request.timingsMaster.data.length) {
				const timed_ticks = request.timingsMaster.data[index].minuteReports[0].ticks.timedTicks;
				const player_ticks = request.timingsMaster.data[index].minuteReports[0].ticks.playerTicks;
				const players = (player_ticks / timed_ticks);
				max_online_players = Math.max(players, max_online_players);
				index = index + 1;
			}
			if (1000 * max_online_players / parseInt(max_mem) > 6 && parseInt(max_mem) < 10000) fields.push({ name: '❌ Low Memory', value: 'You should be using more RAM with this many players.', inline: true });
			if (flags.includes('-Xms')) {
				let min_mem = 0;
				flaglist.forEach(flag => {
					if (flag.startsWith('-Xmx')) {
						min_mem = flag.split('-Xmx')[1];
						min_mem = min_mem.replace('G', '000');
						min_mem = min_mem.replace('M', '');
						min_mem = min_mem.replace('g', '000');
						min_mem = min_mem.replace('m', '');
					}
				});
				if (min_mem != max_mem) fields.push({ name: '❌ Aikar\'s Flags', value: 'Your Xmx and Xms values should be equal when using Aikar\'s flags.', inline: true });
			}
		}
	}
	else if (flags.includes('-Dusing.aikars.flags=mcflags.emc.gs')) {
		fields.push({ name: '❌ Outdated Flags', value: 'Update [Aikar\'s flags](https://aikar.co/2018/07/02/tuning-the-jvm-g1gc-garbage-collector-flags-for-minecraft/).', inline: true });
	}
	else {
		fields.push({ name: '❌ Aikar\'s Flags', value: 'Use [Aikar\'s flags](https://aikar.co/2018/07/02/tuning-the-jvm-g1gc-garbage-collector-flags-for-minecraft/).', inline: true });
	}

	const cpu = parseInt(request.timingsMaster.system.cpu);
	if (cpu <= 2) fields.push({ name: '❌ Threads', value: `You only have ${cpu} thread(s). Find a [better host](https://www.birdflop.com).`, inline: true });

	const handlers = Object.keys(request_raw.idmap.handlers).map(i => { return request_raw.idmap.handlers[i]; });
	handlers.forEach(handler => {
		let handler_name = handler[1];
		if (handler_name.startsWith('Command Function - ') && handler_name.endsWith(':tick')) {
			handler_name = handler_name.split('Command Function - ')[1].split(':tick')[0];
			fields.push({ name: `❌ ${handler_name}`, value: 'This datapack uses command functions which are laggy.', inline: true });
		}
	});

	if (TIMINGS_CHECK.plugins) {
		Object.keys(TIMINGS_CHECK.plugins).forEach(server_name => {
			if (Object.keys(request.timingsMaster.config).includes(server_name)) {
				plugins.forEach(plugin => {
					Object.keys(TIMINGS_CHECK.plugins[server_name]).forEach(plugin_name => {
						if (plugin.name == plugin_name) {
							const stored_plugin = TIMINGS_CHECK.plugins[server_name][plugin_name];
							stored_plugin.name = plugin_name;
							fields.push(createField(stored_plugin));
						}
					});
				});
			}
		});
	}
	if (TIMINGS_CHECK.config) {
		Object.keys(TIMINGS_CHECK.config).map(i => { return TIMINGS_CHECK.config[i]; }).forEach(config => {
			Object.keys(config).forEach(option_name => {
				const option = config[option_name];
				evalField(fields, option, option_name, plugins, server_properties, bukkit, spigot, paper, pufferfish, purpur, client);
			});
		});
	}

	plugins.forEach(plugin => {
		if (plugin.authors && plugin.authors.toLowerCase().includes('songoda')) {
			if (plugin.name == 'EpicHeads') fields.push({ name: '❌ EpicHeads', value: 'This plugin was made by Songoda. Songoda is sketchy. You should find an alternative such as [HeadsPlus](https://spigotmc.org/resources/headsplus-»-1-8-1-16-4.40265/) or [HeadDatabase](https://www.spigotmc.org/resources/head-database.14280/).', inline: true });
			else if (plugin.name == 'UltimateStacker') fields.push({ name: '❌ UltimateStacker', value: 'Stacking plugins actually causes more lag.\nRemove UltimateStacker.', inline: true });
			else fields.push({ name: `❌ ${plugin.name}`, value: 'This plugin was made by Songoda. Songoda is sketchy. You should find an alternative.', inline: true });
		}
	});

	const worlds = request_raw.worlds ? Object.keys(request_raw.worlds).map(i => { return request_raw.worlds[i]; }) : [];
	let high_mec = false;
	worlds.forEach(world => {
		const max_entity_cramming = parseInt(world.gamerules.maxEntityCramming);
		if (max_entity_cramming >= 24) high_mec = true;
	});
	if (high_mec) fields.push({ name: '❌ maxEntityCramming', value: 'Decrease this by running the /gamerule command in each world. Recommended: 8.', inline: true });

	const normal_ticks = request.timingsMaster.data[0].totalTicks;
	let worst_tps = 20;
	request.timingsMaster.data.forEach(data => {
		const total_ticks = data.totalTicks;
		if (total_ticks == normal_ticks) {
			const end_time = data.end;
			const start_time = data.start;
			let tps;
			if (end_time == start_time) tps = 20;
			else tps = total_ticks / (end_time - start_time);
			if (tps < worst_tps) worst_tps = tps;
		}
	});
	let red = 0;
	let green = 0;
	if (worst_tps < 10) {
		red = 255;
		green = 255 * (0.1 * worst_tps);
	}
	else {
		red = 255 * (-0.1 * worst_tps + 2);
		green = 255;
	}

	function componentToHex(c) {
		const hex = c.toString(16);
		return hex.length == 1 ? '0' + hex : hex;
	}
	TimingsEmbed.setColor(parseInt('0x' + componentToHex(Math.round(red)) + componentToHex(Math.round(green)) + '00'));

	if (timing_cost > 500) {
		const suggestions = fields.length - 1;
		TimingsEmbed.setColor(0xff0000).setDescription('')
			.setFields([{ name: '❌ Timingcost (URGENT)', value: `Your timingcost is ${timing_cost}. This value would be at most 200 on a reasonable server. Your cpu is critically overloaded and/or slow. Hiding ${suggestions} comparitively negligible suggestions until you resolve this fundamental problem. Find a [better host](https://www.birdflop.com).`, inline: true }]);
		return [{ embeds: [TimingsEmbed] }];
	}

	if (fields.length == 0) {
		TimingsEmbed.addFields([{ name: '✅ All good', value: 'Analyzed with no recommendations.' }]);
		return [{ embeds: [TimingsEmbed] }];
	}
	const components = [];
	const issues = [...fields];
	if (issues.length >= 13) {
		fields.splice(12, issues.length, { name: `Plus ${issues.length - 12} more recommendations`, value: 'Click the buttons below to see more' });
		TimingsEmbed.setFooter({ text: `Requested by ${(message.author ?? message.member.user).tag} • Page 1 of ${Math.ceil(issues.length / 12)}`, iconURL: (message.author ?? message.member.user).avatarURL() });
		components.push(
			new MessageActionRow()
				.addComponents([
					new MessageButton()
						.setCustomId('timings_prev')
						.setEmoji({ name: '⬅️' })
						.setStyle('SECONDARY'),
					new MessageButton()
						.setCustomId('timings_next')
						.setEmoji({ name: '➡️' })
						.setStyle('SECONDARY'),
					new MessageButton()
						.setURL('https://github.com/pemigrade/botflop')
						.setLabel('Botflop')
						.setStyle('LINK'),
				]),
		);
	}
	TimingsEmbed.addFields(fields);
	return [{ embeds: [TimingsEmbed], components: components }, issues];
};
