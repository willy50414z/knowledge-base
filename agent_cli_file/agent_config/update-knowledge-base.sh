#!/bin/bash
git submodule update --init --remote --merge knowledge-base
git -C knowledge-base submodule update --init --remote --recursive
