#   Copyright (c) 2020  PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from x2paddle.optimizer.pass_manager import PassManager
from x2paddle.optimizer.fusion.dygraph import *
from x2paddle.optimizer.fusion.static import *
from x2paddle.optimizer.elimination.dygraph import *
from x2paddle.optimizer.elimination.static import *

class GraphOptimizer(object):
    def __init__(self, source_frame, paddle_type="dygraph", jit_type="trace"):
        if source_frame == "pytorch":
            if jit_type == "trace":
                self.passes = ["trace_fc_fuse_pass"]
            else:
                self.passes = [
                    "dygraph_constant_fuse_pass", 
                    "dygraph_batchnorm2d_fuse_pass",
                    "dygraph_interpolate_bilinear_fuse_pass", 
                    "dygraph_fc_fuse_pass",
                    "dygraph_adaptive_pool2d_fuse_pass", 
                    "dygraph_reshape_fuse_pass",
                    "dygraph_dropout_fuse_pass"
                ]
        elif source_frame == "caffe":
            if paddle_type == "dygraph":
                self.passes = ["dygraph_bn_scale_fuse_pass"]
            else:
                self.passes = ["static_bn_scale_fuse_pass"]
        elif source_frame == "tf":
            if paddle_type == "dygraph":
                self.passes = [
                    "dygraph_conv2d_add_fuse_pass",
                    "dygraph_tf_batchnorm_fuse_pass",
                    "dygraph_prelu_fuse_pass",
                    "transpose_eliminate_pass"
                ]
            else:
                self.passes = [
                    "static_conv2d_add_fuse_pass",
                    "static_tf_batchnorm_fuse_pass",
                    "static_prelu_fuse_pass",
                    "static_transpose_eliminate_pass"
                ]
        else:
            self.passes = []

    def optimize(self, graph):
        for pass_name in self.passes:
            pass_ = PassManager.lookup(pass_name)()
            if pass_name.endswith("_eliminate_pass"):
                pass_.apply(graph)
            else:
                while True:
                    before_len = len(graph.layers)
                    pass_.apply(graph)
                    after_len = len(graph.layers)
                    if before_len == after_len:
                        break
            print("{} done!".format(pass_name))
        return graph
