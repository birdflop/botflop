import {
  ComponentType,
  ButtonInteraction,
  ContainerBuilder,
  MessageFlags,
  TextDisplayBuilder,
  SectionBuilder,
} from 'discord.js';
import type { Command } from '~/lists/Objects';

export const privacy: Command = {
  description: "View the bot's privacy policy.",
  cooldown: 10,
  async execute(interaction, client) {
    try {
      // Create container with ping information and add ping again button
      const PingContainer = new ContainerBuilder()
        .setAccentColor(0x5865f2)
        .addSectionComponents((section) =>
          section.addTextDisplayComponents((textDisplay) =>
            textDisplay.setContent('# Privacy Policy')
          )
        )
        .addSeparatorComponents((separator) => separator)
        .addTextDisplayComponents((textDisplay) =>
          textDisplay.setContent(
            "You can view the bot's privacy policy at https://bin.birdflop.com/apezizinip.txt."
          )
        );

      // reply
      const pingmsg = await interaction.reply({
        components: [PingContainer],
        flags: MessageFlags.IsComponentsV2,
      });

      // create collector for ping again button
      const filter = (i: ButtonInteraction) => i.customId == 'ping_again';
      const collector =
        pingmsg.createMessageComponentCollector<ComponentType.Button>({
          filter,
          time: 30000,
        });
      collector.on('collect', async (btnint) => {
        // Check if the button is one of the settings buttons
        await btnint.deferUpdate();

        // Set the description with new ping stuff
        const DescriptionComponent = PingContainer
          .components[2] as TextDisplayBuilder;
        DescriptionComponent.setContent(
          `**Message Latency** ${Date.now() - interaction.createdTimestamp}ms\n**API Latency** ${client.ws.ping}ms`
        );

        // Get the current title, get the next one from the pong array, and set it
        const TitleSection = PingContainer.components[0] as SectionBuilder;
        const TitleComponent = TitleSection.components[0] as TextDisplayBuilder;

        // Set title and update message
        TitleComponent.setContent('# Pong!');
        await btnint.editReply({ components: [PingContainer] });
      });

      // When the collector stops, remove refresh button from it
      collector.on('end', () => {
        // get title section and replace it with just the title component to remove the button from the container
        const TitleSection = PingContainer.components[0] as SectionBuilder;
        const TitleComponent = TitleSection.components[0] as TextDisplayBuilder;
        PingContainer.components[0] = TitleComponent;

        interaction.editReply({ components: [PingContainer] });
      });
    } catch (err) {
      error(err, interaction);
    }
  },
};
