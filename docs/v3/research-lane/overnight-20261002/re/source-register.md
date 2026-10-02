# R-E public source register

All 39 entries are primary documentation. Retrieved 2026-10-02 UTC. Live URLs are not immutable; a date/version pin records the reviewed reference edition, not a measured operating-system profile. Null publication dates in JSON remain unknown; retrieval date is not substituted for publication. No private capture paths appear here.

## W01 — Access control model
- Publisher: Microsoft Learn / Microsoft
- Link: [Access control model](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-control-model)
- Pin: Live Win32 documentation snapshot inspected 2026-10-02; not immutable
- Source date: 2025-07-10; retrieved 2026-10-02
- Supports: Windows access-control model and securable objects
- Limit: No process-specific grant inventory or native behavior measured

## W02 — Process Security and Access Rights
- Publisher: Microsoft Learn / Microsoft
- Link: [Process Security and Access Rights](https://learn.microsoft.com/en-us/windows/win32/procthread/process-security-and-access-rights)
- Pin: Live Win32 documentation snapshot inspected 2026-10-02; not immutable
- Source date: 2025-07-14; retrieved 2026-10-02
- Supports: PROCESS_VM_READ/WRITE, DUP_HANDLE, CREATE_THREAD, DACL checks and SeDebugPrivilege
- Limit: Protected-process exceptions and effective privileges must be profiled

## W03 — Mandatory Integrity Control
- Publisher: Microsoft Learn / Microsoft
- Link: [Mandatory Integrity Control](https://learn.microsoft.com/en-us/windows/win32/secauthz/mandatory-integrity-control)
- Pin: Live Win32 documentation snapshot inspected 2026-10-02; not immutable
- Source date: 2025-07-08; retrieved 2026-10-02
- Supports: Integrity labels and default NO_WRITE_UP rather than general confidentiality
- Limit: No blanket claim that low integrity denies all reads

## W04 — AppContainer isolation
- Publisher: Microsoft Learn / Microsoft
- Link: [AppContainer isolation](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation)
- Pin: Live Win32 documentation snapshot inspected 2026-10-02; not immutable
- Source date: 2025-07-08; retrieved 2026-10-02
- Supports: App/user identity and constrained resource/process access
- Limit: Vendor isolation description is not local CLI compatibility or reverse parent isolation evidence

## W05 — CryptProtectData
- Publisher: Microsoft Learn / Microsoft
- Link: [CryptProtectData](https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata)
- Pin: Live Win32 documentation snapshot inspected 2026-10-02; not immutable
- Source date: 2026-05-15; retrieved 2026-10-02
- Supports: User-logon DPAPI scope; machine flag permits any local user to decrypt accessible blobs
- Limit: Encryption at rest is not same-user application isolation

## W06 — CredReadW
- Publisher: Microsoft Learn / Microsoft
- Link: [CredReadW](https://learn.microsoft.com/en-us/windows/win32/api/wincred/nf-wincred-credreadw)
- Pin: Live Win32 documentation snapshot inspected 2026-10-02; not immutable
- Source date: 2024-11-20; retrieved 2026-10-02
- Supports: Credential set associated with current token logon session
- Limit: Exact credential type and store behavior untested

## W07 — Named Pipe Security and Access Rights
- Publisher: Microsoft Learn / Microsoft
- Link: [Named Pipe Security and Access Rights](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights)
- Pin: Live Win32 documentation snapshot inspected 2026-10-02; not immutable
- Source date: 2021-01-07; retrieved 2026-10-02
- Supports: Explicit/default DACL, access checks and generic-write/create-instance issue
- Limit: Locality and opaque name are not task authorization

## W08 — CreateProcessAsUserW
- Publisher: Microsoft Learn / Microsoft
- Link: [CreateProcessAsUserW](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessasuserw)
- Pin: Live Win32 documentation snapshot inspected 2026-10-02; not immutable
- Source date: 2023-02-09; retrieved 2026-10-02
- Supports: Target token, privileges, full-access returned process handle, environment/session/desktop handling
- Limit: API exists below floor; no floor-specific process launch exercised

## W09 — Inheritance (Processes and Threads)
- Publisher: Microsoft Learn / Microsoft
- Link: [Inheritance (Processes and Threads)](https://learn.microsoft.com/en-us/windows/win32/procthread/inheritance)
- Pin: Live Win32 documentation snapshot inspected 2026-10-02; not immutable
- Source date: 2025-07-14; retrieved 2026-10-02
- Supports: Handle/environment/console inheritance
- Limit: A clean environment does not close other inherited capabilities

## W10 — Restricted Tokens
- Publisher: Microsoft Learn / Microsoft
- Link: [Restricted Tokens](https://learn.microsoft.com/en-us/windows/win32/secauthz/restricted-tokens)
- Pin: Live Win32 documentation snapshot inspected 2026-10-02; not immutable
- Source date: 2021-01-07; retrieved 2026-10-02
- Supports: Privilege removal, deny-only/restricting SIDs, two access checks and desktop warning
- Limit: Restrictions must cover every R thread/process and accessible helper

## W11 — Interactive Services
- Publisher: Microsoft Learn / Microsoft
- Link: [Interactive Services](https://learn.microsoft.com/en-us/windows/win32/services/interactive-services)
- Pin: Live Win32 documentation snapshot inspected 2026-10-02; not immutable
- Source date: 2021-01-07; retrieved 2026-10-02
- Supports: Session 0, noninteractive service model and privileged desktop warning
- Limit: No authenticated CLI renewal/session compatibility measured

## W12 — Security Considerations for Assistive Technologies
- Publisher: Microsoft Learn / Microsoft
- Link: [Security Considerations for Assistive Technologies](https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-securityoverview)
- Pin: Live Win32 documentation snapshot inspected 2026-10-02; not immutable
- Source date: 2026-02-19; retrieved 2026-10-02
- Supports: UIAccess and cross-process/integrity interaction
- Limit: Does not establish every clipboard/screenshot permission

## W13 — How AccessCheck Works
- Publisher: Microsoft Learn / Microsoft
- Link: [How AccessCheck Works](https://learn.microsoft.com/en-us/windows/win32/secauthz/how-dacls-control-access-to-an-object)
- Pin: Live Win32 documentation snapshot inspected 2026-10-02; not immutable
- Source date: 2021-01-07; retrieved 2026-10-02
- Supports: Requested rights and ordered DACL evaluation
- Limit: Static ACL review alone cannot close indirect execution paths

## W14 — UpdateProcThreadAttribute
- Publisher: Microsoft Learn / Microsoft
- Link: [UpdateProcThreadAttribute](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)
- Pin: Live Win32 documentation snapshot inspected 2026-10-02; not immutable
- Source date: 2022-11-01; retrieved 2026-10-02
- Supports: Explicit inherited HANDLE_LIST, security capability and Job-list creation attributes
- Limit: Native race/containment qualification not performed

## W15 — ImpersonateNamedPipeClient
- Publisher: Microsoft Learn / Microsoft
- Link: [ImpersonateNamedPipeClient](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-impersonatenamedpipeclient)
- Pin: Live Win32 documentation snapshot inspected 2026-10-02; not immutable
- Source date: 2021-10-13; retrieved 2026-10-02
- Supports: Server impersonation of client and required refusal on impersonation failure
- Limit: No blanket assertion of arbitrary pipe-to-admin escalation

## W16 — AppContainer for legacy apps
- Publisher: Microsoft Learn / Microsoft
- Link: [AppContainer for legacy apps](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-for-legacy-applications-)
- Pin: Live Win32 documentation snapshot inspected 2026-10-02; not immutable
- Source date: 2023-07-25; retrieved 2026-10-02
- Supports: Packaged/unpackaged AppContainer use and token inheritance
- Limit: Generic Win32/CLI behavior and required resource grants remain unknown

## W17 — Collecting User-Mode Dumps
- Publisher: Microsoft Learn / Microsoft
- Link: [Collecting User-Mode Dumps](https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps)
- Pin: Live Win32 documentation snapshot inspected 2026-10-02; not immutable
- Source date: 2024-07-18; retrieved 2026-10-02
- Supports: Configurable local full/minidumps, profile paths and ACL implications
- Limit: No dump collection or configuration changes performed

## W18 — Job Objects
- Publisher: Microsoft Learn / Microsoft
- Link: [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
- Pin: Live Win32 documentation snapshot inspected 2026-10-02; not immutable
- Source date: 2025-07-14; retrieved 2026-10-02
- Supports: Membership, default descendants, breakaway, group termination and notification caveats
- Limit: Not credential confidentiality or all-causal-descendant proof

## L01 — user_namespaces(7)
- Publisher: Linux man-pages project (man7.org publication)
- Link: [user_namespaces(7)](https://man7.org/linux/man-pages/man7/user_namespaces.7.html)
- Pin: Linux man-pages 6.19
- Source date: 2026-02-08; retrieved 2026-10-02
- Supports: Namespace ownership, ID maps and capability direction; parent owner capability relationship
- Limit: Documentation release is not a kernel floor; distribution policy unknown

## L02 — mount_namespaces(7)
- Publisher: Linux man-pages project (man7.org publication)
- Link: [mount_namespaces(7)](https://man7.org/linux/man-pages/man7/mount_namespaces.7.html)
- Pin: Linux man-pages 6.19
- Source date: unknown/not stated in inspected excerpt; retrieved 2026-10-02
- Supports: Mount views, bind mounts and propagation
- Limit: Actual mounts/FD closure and policies unobserved

## L03 — pid_namespaces(7)
- Publisher: Linux man-pages project (man7.org publication)
- Link: [pid_namespaces(7)](https://man7.org/linux/man-pages/man7/pid_namespaces.7.html)
- Pin: Linux man-pages 6.19
- Source date: unknown/not stated in inspected excerpt; retrieved 2026-10-02
- Supports: Ancestor visibility, namespace direction and signal caveats
- Limit: Visibility is not authorization or complete containment

## L04 — Kernel Key Retention Service
- Publisher: Linux kernel development community
- Link: [Kernel Key Retention Service](https://docs.kernel.org/6.12/security/keys/core.html)
- Pin: Linux documentation 6.12
- Source date: unknown/not stated in inspected excerpt; retrieved 2026-10-02
- Supports: Key types, permissions/possession, session inheritance and kernel-only logon payload
- Limit: Does not establish a CLI uses keyrings or is compatible with a chosen type

## L05 — Yama
- Publisher: Linux kernel development community
- Link: [Yama](https://docs.kernel.org/6.12/admin-guide/LSM/Yama.html)
- Pin: Linux documentation 6.12
- Source date: unknown/not stated in inspected excerpt; retrieved 2026-10-02
- Supports: ptrace_scope modes, parent debugging and PR_SET_PTRACER exceptions
- Limit: CONFIG/security policy must be fingerprinted; not all proc read checks identical

## L06 — proc_pid_environ(5)
- Publisher: Linux man-pages project (man7.org publication)
- Link: [proc_pid_environ(5)](https://man7.org/linux/man-pages/man5/proc_pid_environ.5.html)
- Pin: Linux man-pages 6.19
- Source date: unknown/not stated in inspected excerpt; retrieved 2026-10-02
- Supports: Initial environment exposure and PTRACE_MODE_READ_FSCREDS permission check
- Limit: No target environment inspected

## L07 — proc_pid_mem(5)
- Publisher: Linux man-pages project (man7.org publication)
- Link: [proc_pid_mem(5)](https://man7.org/linux/man-pages/man5/proc_pid_mem.5.html)
- Pin: Linux man-pages 6.19
- Source date: 2026-02-08; retrieved 2026-10-02
- Supports: Memory access requires PTRACE_MODE_ATTACH_FSCREDS check
- Limit: Denial of one interface does not establish denial of all memory/control paths

## L08 — ptrace(2)
- Publisher: Linux man-pages project (man7.org publication)
- Link: [ptrace(2)](https://man7.org/linux/man-pages/man2/ptrace.2.html)
- Pin: Linux man-pages 6.19
- Source date: unknown/not stated in inspected excerpt; retrieved 2026-10-02
- Supports: Read/attach access modes, credentials, dumpability, capability and LSM checks
- Limit: Different operations and namespaces need exact profile tests

## L09 — Secret Service API Draft
- Publisher: freedesktop.org Secret Service specification authors
- Link: [Secret Service API Draft](https://specifications.freedesktop.org/secret-service/latest-single/)
- Pin: Secret Service 0.2 DRAFT
- Source date: 2026-09-23; retrieved 2026-10-02
- Supports: User-session service, GetSecret/GetSecrets, attributes and no mandated access-control policy
- Limit: Draft interface does not establish implementation ACLs or security of a particular daemon

## L10 — acl(5)
- Publisher: Linux ACL project (upstream manual published by man7.org)
- Link: [acl(5)](https://man7.org/linux/man-pages/man5/acl.5.html)
- Pin: Linux ACL upstream manual; fetched upstream 2026-08-03; most recent commit date shown 2026-06-29
- Source date: 2026-06-05; retrieved 2026-10-02
- Supports: POSIX ACL user/group/mask/default semantics
- Limit: Upstream commit hash not exposed in retrieved page; not a Windows DACL

## L11 — unix(7)
- Publisher: Linux man-pages project (man7.org publication)
- Link: [unix(7)](https://man7.org/linux/man-pages/man7/unix.7.html)
- Pin: Linux man-pages 6.19
- Source date: 2026-02-08; retrieved 2026-10-02
- Supports: Unix socket peer/SCM credentials and SCM_RIGHTS open-file-description transfer
- Limit: IPC peer identity is not task authority; no transport selected

## L12 — Control Group v2
- Publisher: Linux kernel development community
- Link: [Control Group v2](https://docs.kernel.org/6.12/admin-guide/cgroup-v2.html)
- Pin: Linux documentation 6.12
- Source date: unknown/not stated in inspected excerpt; retrieved 2026-10-02
- Supports: Delegated subtree containment, resource control, populated and kill interfaces
- Limit: Membership-limited lifecycle control, not secret confidentiality

## L13 — Control Group v2 (compatibility reference)
- Publisher: Linux kernel development community
- Link: [Control Group v2 (compatibility reference)](https://docs.kernel.org/6.6/admin-guide/cgroup-v2.html)
- Pin: Linux documentation 6.6
- Source date: unknown/not stated in inspected excerpt; retrieved 2026-10-02
- Supports: Compatibility-floor delegation and cgroup-v2 semantics
- Limit: Kernel configuration/backports/permissions still require native evidence

## L14 — capabilities(7)
- Publisher: Linux man-pages project (man7.org publication)
- Link: [capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- Pin: Linux man-pages 6.19
- Source date: 2026-02-08; retrieved 2026-10-02
- Supports: DAC, ptrace and administrative capabilities; effective/permitted/ambient/bounding sets
- Limit: No capability-set or privilege-drop operation executed

## L15 — Seccomp BPF
- Publisher: Linux kernel development community
- Link: [Seccomp BPF](https://docs.kernel.org/6.12/userspace-api/seccomp_filter.html)
- Pin: Linux documentation 6.12
- Source date: unknown/not stated in inspected excerpt; retrieved 2026-10-02
- Supports: Syscall filtering, no-new-privileges, inheritance, architecture and notification caveats; explicitly not a sandbox
- Limit: Source does not guarantee filesystem/information-flow mediation

## L16 — Ubuntu 24.04 LTS release notes
- Publisher: Canonical / Ubuntu release documentation
- Link: [Ubuntu 24.04 LTS release notes](https://documentation.ubuntu.com/release-notes/24.04/)
- Pin: Ubuntu 24.04 LTS release notes; mutable live documentation
- Source date: unknown/not stated in inspected excerpt; retrieved 2026-10-02
- Supports: Initial 6.8 kernel; AppArmor restriction of unprivileged namespace capability use
- Limit: Distribution illustration, not a selected profile or current installed-kernel claim

## L17 — apparmor.d(5), Debian trixie
- Publisher: AppArmor upstream manual / Debian package documentation
- Link: [apparmor.d(5), Debian trixie](https://dyn.manpages.debian.org/trixie/apparmor/apparmor.d.5.en.html)
- Pin: AppArmor 4.1.0; Debian source package 4.1.0-1
- Source date: 2025-04-10; retrieved 2026-10-02
- Supports: User namespace permission and policy controls
- Limit: Does not prove effective defaults on an installed Debian/RHEL machine

## L18 — execve(2)
- Publisher: Linux man-pages project (man7.org publication)
- Link: [execve(2)](https://man7.org/linux/man-pages/man2/execve.2.html)
- Pin: Linux man-pages 6.19
- Source date: unknown/not stated in inspected excerpt; retrieved 2026-10-02
- Supports: Environment, preserved descriptors unless close-on-exec, credential transition constraints
- Limit: No process execution or FD inventory performed

## L19 — core(5)
- Publisher: Linux man-pages project (man7.org publication)
- Link: [core(5)](https://man7.org/linux/man-pages/man5/core.5.html)
- Pin: Linux man-pages 6.19
- Source date: 2026-05-07; retrieved 2026-10-02
- Supports: Memory image dumps, host collection/pipe behavior, RLIMIT_CORE pipe exception
- Limit: No dump produced; later kernel features on page are not imported into 6.6/6.12 floor

## L20 — Landlock: unprivileged access control
- Publisher: Linux kernel development community
- Link: [Landlock: unprivileged access control](https://docs.kernel.org/6.12/userspace-api/landlock.html)
- Pin: Linux documentation 6.12
- Source date: 2024-10; retrieved 2026-10-02
- Supports: Irreversible descendant restrictions, ptrace domain ordering and ABI-specific IPC/network features
- Limit: Additional comparator only; no LSM or sandbox selected; runtime ABI unknown

## L21 — Landlock: unprivileged access control (compatibility reference)
- Publisher: Linux kernel development community
- Link: [Landlock: unprivileged access control (compatibility reference)](https://docs.kernel.org/6.6/userspace-api/landlock.html)
- Pin: Linux documentation 6.6
- Source date: 2022-10; retrieved 2026-10-02
- Supports: Older filesystem-focused interface, restriction inheritance and limits
- Limit: No assumption that newer ABI features exist on 6.6

## Shared platform source supplements

These metadata entries supplement the original 39-source register. Full retrieved-version/hash limitations are in [R-U’s source register](../ru/source-register.json).

- RU-S04: [Windows Job extended limits](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information); Live Win32 API reference
- RU-S05: [Windows Filtering Platform](https://learn.microsoft.com/en-us/windows/win32/fwp/windows-filtering-platform-start-page); Live Win32 platform documentation
- RU-S06: [Windows reparse points](https://learn.microsoft.com/en-us/windows/win32/fileio/reparse-points); Live Win32 filesystem documentation
- RU-S11: [Landlock 6.6 UAPI](https://raw.githubusercontent.com/torvalds/linux/v6.6/include/uapi/linux/landlock.h); Linux tag v6.6; immutable commit not separately resolved
- RU-S12: [Landlock 6.12 UAPI](https://raw.githubusercontent.com/torvalds/linux/v6.12/include/uapi/linux/landlock.h); Linux tag v6.12; immutable commit not separately resolved
- RU-S14: [openat2 manual](https://man7.org/linux/man-pages/man2/openat2.2.html); Linux man-pages live publication; exact page hash not retained
- RU-S15: [clone manual](https://man7.org/linux/man-pages/man2/clone.2.html); Linux man-pages live publication; exact page hash not retained
