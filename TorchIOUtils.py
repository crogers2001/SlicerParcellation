import logging

import slicer
from slicer.ScriptedLoadableModule import (
  ScriptedLoadableModule,
  ScriptedLoadableModuleLogic,
)
import sitkUtils as su


class TorchIOUtils(ScriptedLoadableModule):
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "TorchIO Utils"
    self.parent.categories = ["Utilities"]
    self.parent.dependencies = []
    self.parent.contributors = ["Fernando Perez-Garcia (University College London)"]
    self.parent.helpText = 'This module does this and that.'
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = (
      'This work was was funded by the Engineering and Physical Sciences'
      ' Research Council (​EPSRC)'
    )


class TorchIOUtilsLogic(ScriptedLoadableModuleLogic):
  def __init__(self):
    self._torchio = None

  @property
  def torchio(self):
    if self._torchio is None:
      self._torchio = self.importTorchIO()
    return self._torchio

  def importTorchIO(self):
    from PyTorchUtils import PyTorchUtilsLogic
    PyTorchUtilsLogic().torch  # make sure torch is installed
    try:
      import torchio
    except ModuleNotFoundError:
      torchio = self.installTorchIO()
    logging.info(f'TorchIO {torchio.__version__} imported correctly')
    return torchio

  def installTorchIO(self):
    slicer.util.pip_install('torchio')
    import torchio
    logging.info(f'TorchIO {torchio.__version__} installed correctly')
    return torchio

  @staticmethod
  def getTorchIOImageFromVolumeNode(self, volumeNode):
    image = su.PullVolumeFromSlicer(volumeNode)
    tensor, affine = self.torchio.io.sitk_to_nib(image)
    if volumeNode.IsA('vtkMRMLScalarVolumeNode'):
      image = self.torchio.ScalarImage(tensor=tensor, affine=affine)
    elif volumeNode.IsA('vtkMRMLLabelMapVolumeNode'):
      image = self.torchio.LabelMap(tensor=tensor, affine=affine)
    return image

  def getVolumeNodeFromTorchIOImage(self, image, outputVolumeNode):
    su.PushVolumeToSlicer(image.as_sitk(), targetNode=outputVolumeNode)
    return outputVolumeNode
