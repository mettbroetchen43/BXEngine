#######################
# BXEngine            #
# overlaymanager.py   #
# Copyright 2021-2023 #
# Sei Satzparad       #
#######################

# **********
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# **********

from typing import Optional

import pygame

from lib.logger import Logger


class OverlayManager(object):
    """The Overlay Manager

    Keeps track of and draws images that are overlaid onto the base room image.

    :ivar config: This contains the engine's configuration variables.
    :ivar app: The main App instance.
    :ivar resource: The ResourceManager instance.
    :ivar world: The World instance.
    :ivar log: The Logger instance for this class.
    :ivar overlays: A dict of Overlay IDs mapped to overlay images currently in the roomview.
    """
    def __init__(self, config, app, resource, world):
        """OverlayManager Class Initializer

        :param config: This contains the engine's configuration variables.
        :param app: The main App instance.
        :param resource: The ResourceManager instance.
        :param world: The World instance.
        """
        self.config = config
        self.app = app
        self.resource = resource
        self.world = world
        self.log = Logger("Overlay")

        # self.overlays[Overlay_ID] = {
        #     "filename": filename,
        #     "image": pygame.Surface,
        #     "position": [x, y],
        #     "persistent": bool
        # }
        self.overlays = {}

    def insert_overlay(self, imagefile: [str, pygame.Surface], position: tuple[int, int],
                       scale: tuple[float, float] = None, persistent: bool = False) -> Optional[int]:
        """Insert an overlay image into the roomview.

        The image will be inserted at the specified position and scale.

        :param imagefile: The image filename or a Pygame surface loaded through ResourceManager.
        :param position: The X and Y position on the screen to draw the overlay at, as a tuple of floats.
        :param scale: If given, the X and Y scale the overlay should be drawn at, as a tuple of floats.
        :param persistent: Whether the overlay should stay on screen after switching roomviews.

        :return: Integer overlay ID if succeeded, None if failed.
        """
        # Attempt to load the overlay image from a filename.
        if type(imagefile) is str:
            overlay_image = self.resource.load_image("{0}/{1}".format(self.world.dir, imagefile), scale)
            filename = imagefile

        # We were passed a surface pre-loaded from ResourceManager.
        elif type(imagefile) is pygame.Surface:
            overlay_image = imagefile
            if scale:
                overlay_image = pygame.transform.scale(overlay_image, scale)
            filename = None

        # We don't know what this is.
        else:
            self.log.error("insert_overlay(): Invalid image given.")
            return False

        # We were unable to load the background image.
        if not overlay_image:
            self.log.error("insert_overlay(): Unable to load overlay image: {0}".format(overlay_image))
            return None

        # Success.
        self.overlays[id(overlay_image)] = {"filename": filename, "image": overlay_image, "position": position,
                                            "persistent": persistent}
        self.app._render()
        self.log.info("insert_overlay(): Added overlay image: {0} at position: {1}".format(overlay_image, position))
        return id(overlay_image)

    def remove_overlay(self, overlay_id: int) -> bool:
        """Remove an overlay image from the roomview.

        :param overlay_id: The ID of the overlay to remove, which was given as the return value from insert_overlay().

        :return: True if succeeded, False if failed.
        """
        # The overlay does not exist.
        if overlay_id not in self.overlays:
            self.log.error("remove_overlay(): Overlay ID does not exist to remove: ".format(overlay_id))
            return False

        # Success.
        del self.overlays[overlay_id]
        self.app._render()
        self.log.info("remove_overlay(): Removed overlay image with ID: {0}".format(overlay_id))
        return True

    def reposition_overlay(self, overlay_id: int, position: tuple[int, int]) -> bool:
        """Reposition an overlay image on the window.

        :param overlay_id: The ID of the overlay to remove, which was given as the return value from insert_overlay().
        :param position: The X and Y position on the screen to move the overlay to, as a tuple of floats.

        :return: True if succeeded, False if failed.
        """
        # The overlay does not exist.
        if overlay_id not in self.overlays:
            self.log.error("reposition_overlay(): Overlay ID does not exist to reposition: ".format(overlay_id))
            return False

        # Success.
        self.overlays[overlay_id]["position"] = position
        self.app._render()
        self.log.info("reposition_overlay(): Repositioned overlay image with ID: {0} to position: {1}".format(
            overlay_id, position))
        return True

    def rescale_overlay(self, overlay_id: int, scale: tuple[int, int]) -> bool:
        """Rescale an overlay image.

        :param overlay_id: The ID of the overlay to remove, which was given as the return value from insert_overlay().
        :param scale: The X and Y scale the overlay should be redrawn at, as a tuple of floats.

        :return: True if succeeded, False if failed.
        """
        # The overlay does not exist.
        if overlay_id not in self.overlays:
            self.log.error("rescale_overlay(): Overlay ID does not exist to rescale: ".format(overlay_id))
            return False

        # Success.
        self.overlays[overlay_id]["image"] = pygame.transform.scale(self.overlays[overlay_id]["image"], scale)
        self.app._render()
        self.log.info("rescale_overlay(): Rescaled overlay image with ID: {0} to size: {1}".format(
            overlay_id, scale))
        return True

    def _cleanup(self):
        """Delete non-persistent overlay images.
        """
        to_remove = []
        for overlay in self.overlays:
            if not self.overlays[overlay]["persistent"]:
                to_remove.append(overlay)
        for overlay in to_remove:
            del self.overlays[overlay]
