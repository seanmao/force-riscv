#
# Copyright (C) [2020] Futurewei Technologies, Inc.
#
# FORCE-RISCV is licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR
# FIT FOR A PARTICULAR PURPOSE.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Since there will be a significant amount of directory manipulation import the path utils

import sys

from shared.controller import Controller
from shared.task_controller import TaskController
from shared.summary_core import SummaryErrorQueueItem

from shared.control_item import ControlItem, CtrlItmKeys, ControlItemType

from shared.path_utils import PathUtils
from shared.sys_utils import SysUtils
from shared.msg_utils import Msg
# from shared.errors import EInvalidTypeError

class FileController(Controller):

    def __init__( self ):
        super().__init__( )
        # Msg.dbg( "FileController::__init__( )" )


    def load(self, arg_ctrl_item ):
        super().load( arg_ctrl_item )
        # Msg.dbg( "FileController::load()" )
        self.parent_fctrl = self.ctrl_item.file_path()
        # Msg.dbg( "File Path: %s" % ( self.parent_fctrl ))

        #my_content = open( self.parent_fctrl ).read()
        # Msg.dbg( "\n" + my_content )

        try:
            my_content = open( self.parent_fctrl ).read()
        except Exception as arg_ex:
            Msg.err( "Message: %s, Control File Path: %s" % ( str( arg_ex ), self.parent_fctrl ))
            my_err_queue_item = SummaryErrorQueueItem( { "error"  : arg_ex
                                                       , "message": "Control File Not Found ..."
                                                       , "path"   : self.ctrl_item.file_path()
                                                       , "type"   : str( type( arg_ex ))
                                                       } )


            self.ctrl_item.summary().queue.enqueue( my_err_queue_item )
            return False
        finally:
            pass

        try:
            my_glb, my_loc = SysUtils.exec_content( my_content )

        except Exception as arg_ex:
            my_exc_type, my_exc_val, my_exc_tb = sys.exc_info()
            my_ex = arg_ex

            Msg.err( "Message: %s, Control File Path: %s" % ( str( arg_ex ), self.parent_fctrl))
            Msg.blank()

            my_err_queue_item = SummaryErrorQueueItem( { "error"  : arg_ex
                                                       , "message": "Control File not processed..."
                                                       , "path"   : self.ctrl_item.file_path()
                                                       , "type"   : str( my_exc_type )
                                                       } )

            self.ctrl_item.summary().queue.enqueue( my_err_queue_item )
            return False

        finally:
            pass

        self.fcontrol = my_loc["control_items"]
        return True


    def process(self):

        # Msg.dbg( "FileController::process()" )
        # Msg.dbg( "FileController Contents: \n\"" + str( self.fcontrol ) + "\n" )

        try:
            # Msg.lout( my_options["work-dir"], MsgLevel.dbg, "Work Director Stack" )
            # a control file may iterate through to completion according to the amount set in num_runs
            for my_ndx in range( self.ctrl_item.iterations ):

                # my_usr_lbl = Msg.set_label( "user", "FILE-ITERATION" )
                # Msg.user( "Executing %d of %d Iterations, Control File: %s" % ( my_ndx + 1, self.ctrl_item.iterations, self.ctrl_item.file_path() ))
                # Msg.set_label( "user", my_usr_lbl )

                try:
                    my_item_ndx = 0
                    # each item in the control set exists as a dictionary
                    for my_item_dict in self.fcontrol:
                        try:

                            my_item_ndx += 1
                            my_usr_lbl = Msg.set_label( "user", "CTRL-FILE"  )
                            Msg.blank( "user" )
                            Msg.user( "Processing Line: %s" % (str( my_item_dict )))

                            my_ctrl_item = ControlItem()
                            my_ctrl_item.parent_fctrl = self.parent_fctrl
                            my_ctrl_item.fctrl_item   = str( my_item_dict )

                            my_item_dict[CtrlItmKeys.parent_vals], my_parent_data = self.ctrl_item.values()

                            Msg.lout( my_parent_data, "user", "Result Parent Data" )
                            Msg.lout( my_item_dict  , "user", "Result Item Dictionary" )
                            Msg.set_label( "user", my_usr_lbl )

                            # Msg.user( "Processing Updated Line: %s" % (str( my_item_dict )), "CTRL-FILE" )
                            # Msg.user( str( my_parent_data.data() ), "CTRL-FILE" )
                            my_ctrl_item.load( my_item_dict, my_parent_data )

                            my_item_type = my_ctrl_item.item_type()
                            my_controller = None

                            if my_item_type == ControlItemType.TaskItem:
                                # Msg.dbg( "\nControl Item is a Control Task ..." )
                                my_controller = TaskController()

                            elif my_item_type == ControlItemType.FileItem:
                                # Msg.dbg( "\nControl Item is a Control File ..." )
                                my_controller = FileController()

                            else:
                                raise Exception( "\"" + my_fctrl_name + "\": Unknown Item Type ...\nUnable to Process ... " )

                            # Whew! everything is set up and ready to rock and roll, let the dogs out
                            # my_controller.load( my_ctrl_item )
                            # my_controller.process()

                            if my_controller.load( my_ctrl_item ):
                                my_controller.process()

                            # my_controller.load( my_ctrl_item )
                            # my_controller.process()

                            # Msg.dbg( "%s: Controller Creation Complete" % ( my_ctrl_item.fctrl_name ))

                        except TypeError as arg_ex:

                            Msg.err( str(  arg_ex  ))
                            my_err_queue_item = SummaryErrorQueueItem( { "error"  : "Item #%s Contains an Invalid Type" % ( str( my_item_ndx ))
                                                                       , "message": arg_ex
                                                                       , "path"   : self.ctrl_item.file_path()
                                                                       , "type"   : str( type( arg_ex ))
                                                                       } )

                            self.ctrl_item.summary().queue.enqueue( my_err_queue_item )
                            Msg.blank()

                        except FileNotFoundError as arg_ex:

                            Msg.err( str(  arg_ex  ))
                            my_err_queue_item = SummaryErrorQueueItem( { "error"  : arg_ex
                                                                       , "message": "Control File Not Found ..."
                                                                       , "path"   : self.ctrl_item.file_path()
                                                                       , "type"   : str( type( arg_ex ))
                                                                       } )

                            self.ctrl_item.summary().queue.enqueue( my_err_queue_item )
                            Msg.blank()

                        except Exception as arg_ex:
                            Msg.error_trace( str(arg_ex) )
                            Msg.err( str(arg_ex))
                            Msg.blank()

                        finally:
                            my_controller = None
                            my_item_dict = None

                except Exception as arg_ex:
                    Msg.error_trace( "[ERROR] - " + str(arg_ex) )
                    Msg.err( str(arg_ex))
                finally:
                    pass

        finally:
            pass
            # Msg.dbg()

        return True

