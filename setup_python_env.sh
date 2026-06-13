#!/bin/bash
#=============================================================================
# 脚本名称: setup_env_and_install_file_core.sh
# 描  述:   一键部署 Python 3.9 环境 + OceanBase 驱动 + 离线依赖包
# 用  法:   以 root 用户执行: bash setup_env_and_install_file_core.sh
# 前  提:   1. 当前用户为 root
#           2. python-3.9.13.zip 放在与脚本同目录
#           3. libobclient / obci 两个 rpm 放在与脚本同目录
#           4. file-core-all-whl.zip 放在与脚本同目录
#=============================================================================

set -euo pipefail

#----------------------------- 颜色 & 日志 -----------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

#----------------------------- 变量定义 -------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PHFUND_HOME="/home/phfund"
SOFTWARE_DIR="${PHFUND_HOME}/software"
PYTHON_DIR="${SOFTWARE_DIR}/python-3.9.13"
OBCLIENT_LIB="/u01/obclient/lib"
OBCLIENT_PYTHON="/u01/obclient/python"

#----------------------------- 前置检查 -------------------------------------
prerequisite_check() {
    if [[ "$(id -u)" -ne 0 ]]; then
        error "请以 root 用户执行此脚本！"
        exit 1
    fi

    if ! id -u phfund &>/dev/null; then
        error "用户 phfund 不存在，请先创建该用户！"
        exit 1
    fi

    local missing=0
    for f in python-3.9.13.zip \
             libobclient-2.2.11.1-52025091715.el7.x86_64.rpm \
             obci-2.1.1.1-82025092415.el7.x86_64;do

        if [[ ! -f "${SCRIPT_DIR}/${f}" ]]; then
            error "缺少文件: ${SCRIPT_DIR}/${f}"
            missing=1
        fi
    done

    if [[ "${missing}" -eq 1 ]]; then
        error "请将上述缺失文件放到 ${SCRIPT_DIR} 目录后重试。"
        exit 1
    fi

    info "前置检查通过"
}

###############################################################################
# 一、Python 环境搭建
###############################################################################

step1_install_python() {
    info "====== 步骤1: 拷贝并解压 Python ======"

    # 创建目录
    if [[ ! -d "${SOFTWARE_DIR}" ]]; then
        mkdir -p "${SOFTWARE_DIR}"
        chown phfund:phfund "${SOFTWARE_DIR}"
        info "创建目录 ${SOFTWARE_DIR}"
    fi

    # 拷贝 zip
    if [[ ! -d "${PYTHON_DIR}" ]]; then
        cp "${SCRIPT_DIR}/python-3.9.13.zip" "${SOFTWARE_DIR}/"
        chown phfund:phfund "${SOFTWARE_DIR}/python-3.9.13.zip"
        info "已拷贝 python-3.9.13.zip → ${SOFTWARE_DIR}/"

        # 以 phfund 身份解压
        su - phfund -c "cd ${SOFTWARE_DIR} && unzip -o python-3.9.13.zip"
        info "解压完成"
    else
        warn "${PYTHON_DIR} 已存在，跳过解压"
    fi
}

step2_configure_env() {
    info "====== 步骤2: 配置环境变量 ======"

    su - phfund -c '
        touch ~/.bash_profile

        # 避免重复添加 python lib
        if ! grep -q "python-3.9.13/lib" ~/.bash_profile; then
            sed -i "/^export LD_LIBRARY_PATH/ s|$|:/home/phfund/software/python-3.9.13/lib|" ~/.bash_profile 2>/dev/null || true

            # 如果 sed 没有匹配到已有行，则在末尾追加
            if ! grep -q "python-3.9.13/lib" ~/.bash_profile; then
                cat >> ~/.bash_profile << "PYEOF"

                export LD_LIBRARY_PATH=/home/phfund/software/python-3.9.13/lib:$LD_LIBRARY_PATH
                export PATH=/home/phfund/software/python-3.9.13/bin:$PATH
PYEOF
            fi
            echo "[INFO] 已添加 Python 环境变量"
        else
            echo "[WARN] Python 环境变量已存在，跳过"
        fi

        source ~/.bash_profile
    '
    info "phfund 用户环境变量已配置"
}

step3_create_symlinks() {
    info "====== 步骤3: 创建软链接 (root) ======"

    local bin_dir="${PYTHON_DIR}/bin"

    for pair in "python3.9:python3.9" "pip3.9:pip3.9" "python3.9:python3" "pip3.9:pip3"; do
        src="${bin_dir}/${pair%%:*}"
        dst="/usr/bin/${pair##*:}"
        backup="${dst}.bak.$(date +%Y%m%d%H%M%S)"
        if [[ -L "${dst}" || -e "${dst}" ]]; then
            mv "${dst}" "${backup}"
            warn "${dst} 已存在，备份为 ${backup}"
        fi
        ln -s "${src}" "${dst}"
        info "ln -s ${src} ${dst}"
    done
}

step4_verify_python() {
    info "====== 步骤4: 验证 Python ======"

    if su - phfund -c 'python3 --version' 2>/dev/null; then
        info "python3 安装验证通过"
    else
        error "python3 验证失败，请检查安装"
        exit 1
    fi

    if su - phfund -c ' pip3 --version' 2>/dev/null; then
        info "pip3 安装验证通过"
    else
        error "pip3 验证失败，请检查安装"
        exit 1
    fi
}

###############################################################################
# 二、安装 OceanBase 驱动
###############################################################################

step5_install_obclient_rpm() {
    info "====== 步骤5: 安装 libobclient 和 OBCI (root) ======"

    # 卸载旧版本（忽略不存在的报错）
    rpm -e libobclient 2>/dev/null || true
    rpm -e obci        2>/dev/null || true

    # 安装新版本
    rpm -ivh "${SCRIPT_DIR}/libobclient-2.2.11.1-52025091715.el7.x86_64.rpm"
    info "libobclient 安装完成"

    rpm -ivh "${SCRIPT_DIR}/obci-2.1.1.1-82025092415.el7.x86_64"
    info "obci 安装完成"

    # 版本校验
    local lib_ver obci_ver
    lib_ver=$(rpm -q libobclient 2>/dev/null || echo "未安装")
    obci_ver=$(rpm -q obci        2>/dev/null || echo "未安装")
    info "libobclient 版本: ${lib_ver}"
    info "obci 版本:        ${obci_ver}"
}

step6_install_cx_oracle() {
    info "====== 步骤6: 安装 cx_Oracle 驱动 ======"

    # 解压 OceanBase 官方提供的 cx_Oracle
    if [[ ! -d "${OBCLIENT_PYTHON}/cx_Oracle-8.3.0" ]]; then
        cd "${OBCLIENT_PYTHON}"
        tar -xvf cx_Oracle-8.3.0.tar.gz
        info "解压 ${OBCLIENT_PYTHON}/cx_Oracle-8.3.0.tar.gz 完成"
    else
        warn "cx_Oracle-8.3.0 目录已存在，跳过解压"
    fi

    # 修改权限
    chown -R phfund:phfund "${OBCLIENT_PYTHON}/cx_Oracle-8.3.0"
    info "cx_Oracle-8.3.0 权限已改为 phfund"

    # 以 phfund 用户安装
    su - phfund -c "
        cd ${OBCLIENT_PYTHON}/cx_Oracle-8.3.0
        python3 setup.py install
    "
    info "cx_Oracle 安装完成"

    # 验证
    su - phfund -c "pip3 list 2>/dev/null | grep -i cx-Oracle" && \
        info "cx_Oracle 已在 pip3 list 中" || \
        warn "cx_Oracle 未在 pip3 list 中找到，请检查"
}

step7_configure_ob_env() {
    info "====== 步骤7: 配置 OceanBase 环境变量 ======"

    su - phfund -c '
        touch ~/.bash_profile

        # 添加 obclient lib 到 LD_LIBRARY_PATH
        if ! grep -q "/u01/obclient/lib" ~/.bash_profile; then
            cat >> ~/.bash_profile << "OBEOF"

export LD_LIBRARY_PATH=/u01/obclient/lib/:$LD_LIBRARY_PATH
OBEOF
            echo "[INFO] 已添加 /u01/obclient/lib 到 LD_LIBRARY_PATH"
        else
            echo "[WARN] /u01/obclient/lib 已在配置中，跳过"
        fi

        source ~/.bash_profile
    '

    # 打印最终 LD_LIBRARY_PATH 应该的样子
    info "最终 LD_LIBRARY_PATH 应为:"
    info "  export LD_LIBRARY_PATH=/u01/obclient/lib/:/home/phfund/software/python-3.9.13/lib:\$LD_LIBRARY_PATH"
}

###############################################################################
# 三、安装离线依赖包
###############################################################################

step8_install_whl() {
    info "====== 步骤8: 安装 whl 离线包 ======"

    local whl_dir="${PHFUND_HOME}/file-core-all-whl"

    # 解压 whl 包
    if [[ ! -d "${whl_dir}" ]]; then
        mkdir -p "${whl_dir}"
        chown phfund:phfund "${whl_dir}"
        su - phfund -c "cd ${PHFUND_HOME} && unzip -o ${SCRIPT_DIR}/file-core-all-whl.zip -d file-core-all-whl"
        info "解压 file-core-all-whl.zip 完成"
    else
        warn "${whl_dir} 已存在，跳过解压"
    fi

    # 批量安装 whl
    su - phfund -c "cd ${whl_dir} && pip3 install *.whl --no-deps"
    info "whl 包安装完成"
}

step9_install_targz() {
    info "====== 步骤9: 安装 tar.gz 包 (ratelimit & simpledbf) ======"

    local whl_dir="${PHFUND_HOME}/file-core-all-whl"

    for pkg in ratelimit-2.2.1 simpledbf-0.2.6; do
        local tarball="${whl_dir}/${pkg}.tar.gz"
        local src_dir="${whl_dir}/${pkg}"

        if [[ ! -f "${tarball}" ]]; then
            warn "${tarball} 不存在，跳过 ${pkg}"
            continue
        fi

        # 解压
        if [[ ! -d "${src_dir}" ]]; then
            su - phfund -c "cd ${whl_dir} && tar -xvzf ${pkg}.tar.gz"
            info "解压 ${pkg}.tar.gz 完成"
        else
            warn "${src_dir} 已存在，跳过解压"
        fi

        # 安装
        su - phfund -c "cd ${src_dir} && python3 setup.py install"
        info "${pkg} 安装完成"
    done

    # 验证
    info "====== 验证离线依赖 ======"
    su - phfund -c "pip3 list 2>/dev/null | grep -iE 'ratelimit|simpledbf'" && \
        info "ratelimit 和 simpledbf 均已安装" || \
        warn "ratelimit 或 simpledbf 未找到，请检查"
}

###############################################################################
# 主流程
###############################################################################

main() {
    echo ""
    echo "============================================"
    echo "  一键部署: Python + OceanBase驱动"
    echo "============================================"
    echo ""

    prerequisite_check

    echo ""
    info "========== 一、Python 环境搭建 =========="
    step1_install_python
    step2_configure_env
    step3_create_symlinks
    step4_verify_python

    echo ""
    info "========== 二、安装 OceanBase 驱动 =========="
    step5_install_obclient_rpm
    step6_install_cx_oracle
    step7_configure_ob_env

#    echo ""
#    info "========== 三、安装离线依赖包 =========="
##    step8_install_whl
##    step9_install_targz

    echo ""
    echo "============================================"
    info "全部安装完成！"
    echo "============================================"
    echo ""
    info "请 phfund 用户重新登录后执行以下命令确认环境:"
    info "  python3 --version"
    info "  pip3 --version"
    info "  pip3 list | grep -iE 'cx-Oracle|ratelimit|simpledbf'"
    info "  echo \$LD_LIBRARY_PATH"
}

main "$@"
