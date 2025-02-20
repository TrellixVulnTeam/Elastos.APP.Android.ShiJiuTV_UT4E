/*
 * Copyright (C) 2017 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef SRC_BASE_TEST_TEST_TASK_RUNNER_H_
#define SRC_BASE_TEST_TEST_TASK_RUNNER_H_

#include <sys/select.h>

#include <functional>
#include <list>
#include <map>
#include <string>

#include "perfetto/base/build_config.h"
#include "perfetto/base/thread_checker.h"
#include "perfetto/base/unix_task_runner.h"

#if BUILDFLAG(OS_ANDROID)
#include "perfetto/base/android_task_runner.h"
#endif

namespace perfetto {
namespace base {

#if BUILDFLAG(OS_ANDROID)
using PlatformTaskRunner = AndroidTaskRunner;
#else
using PlatformTaskRunner = UnixTaskRunner;
#endif

class TestTaskRunner : public TaskRunner {
 public:
  TestTaskRunner();
  ~TestTaskRunner() override;

  void RunUntilIdle();
  void __attribute__((__noreturn__)) Run();

  std::function<void()> CreateCheckpoint(const std::string& checkpoint);
  void RunUntilCheckpoint(const std::string& checkpoint, int timeout_ms = 5000);

  // TaskRunner implementation.
  void PostTask(std::function<void()> closure) override;
  void PostDelayedTask(std::function<void()>, int delay_ms) override;
  void AddFileDescriptorWatch(int fd, std::function<void()> callback) override;
  void RemoveFileDescriptorWatch(int fd) override;

 private:
  TestTaskRunner(const TestTaskRunner&) = delete;
  TestTaskRunner& operator=(const TestTaskRunner&) = delete;

  void QuitIfIdle();

  std::string pending_checkpoint_;
  std::map<std::string, bool> checkpoints_;

  PlatformTaskRunner task_runner_;
  ThreadChecker thread_checker_;
};

}  // namespace base
}  // namespace perfetto

#endif  // SRC_BASE_TEST_TEST_TASK_RUNNER_H_
