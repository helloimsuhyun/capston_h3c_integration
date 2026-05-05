import numpy as np
import pyroomacoustics as pra
from scipy import signal

try:
    from nara_wpe.wpe import wpe
except Exception:
    wpe = None


class WpeMusicDoaEstimator:
    def __init__(
        self,
        sample_rate: int = 16000,
        nfft: int = 256,
        mic_radius: float = 0.032,
        mic_channel_indices=(0, 1, 2, 3),
        hardware_offset_deg: float = -135.0,
        wpe_taps: int = 5,
        wpe_delay: int = 2,
        wpe_iterations: int = 3,
    ):
        self.sample_rate = int(sample_rate)
        self.nfft = int(nfft)
        self.mic_channel_indices = tuple(mic_channel_indices)
        self.hardware_offset_deg = float(hardware_offset_deg)

        self.wpe_taps = int(wpe_taps)
        self.wpe_delay = int(wpe_delay)
        self.wpe_iterations = int(wpe_iterations)

        # refined_doa_wpe_iterations가 0 이하이면 WPE를 완전히 생략한다.
        self.use_wpe = self.wpe_iterations > 0

        num_mics = len(self.mic_channel_indices)

        if num_mics < 2:
            raise ValueError(
                f"MUSIC DOA requires at least 2 microphones, got {num_mics}"
            )

        # 현재 코드는 선택된 마이크들이 원형으로 균등 배치되어 있다고 가정한다.
        # mic_channel_indices=(0,1,2,3) 이면 0, 90, 180, 270도 위치로 가정한다.
        angles = np.linspace(0, 2 * np.pi, num_mics, endpoint=False)

        self.mic_locs = np.c_[
            mic_radius * np.cos(angles),
            mic_radius * np.sin(angles),
            np.zeros(num_mics)
        ].T

        self.doa_engine = pra.doa.algorithms["MUSIC"](
            self.mic_locs,
            self.sample_rate,
            self.nfft,
            c=343.0,
            num_src=1
        )

    @staticmethod
    def wrap_deg_pm180(angle_deg: float) -> float:
        while angle_deg > 180.0:
            angle_deg -= 360.0
        while angle_deg <= -180.0:
            angle_deg += 360.0
        return angle_deg

    def estimate(self, audio_multich: np.ndarray) -> float:
        """
        Parameters
        ----------
        audio_multich:
            shape = (num_samples, num_input_channels)

        Returns
        -------
        float
            hardware_offset_deg 보정만 적용된 native angle.
            범위는 -180 ~ 180 deg.
            최종 front_offset, invert_sign 리매핑은 audio_frontend_node.py에서 수행한다.
        """
        if audio_multich.ndim != 2:
            raise ValueError(
                f"audio_multich must be 2-D, got shape={audio_multich.shape}"
            )

        if audio_multich.shape[1] <= max(self.mic_channel_indices):
            raise ValueError(
                f"audio_multich has only {audio_multich.shape[1]} channels, "
                f"but mic_channel_indices={self.mic_channel_indices}"
            )

        # x shape: (num_mics, num_samples)
        x = audio_multich[:, self.mic_channel_indices].astype(np.float32).T

        if x.shape[1] < self.nfft:
            raise ValueError(
                f"not enough samples for STFT: {x.shape[1]} < {self.nfft}"
            )

        # Zxx shape: (num_mics, num_freq_bins, num_frames)
        _, _, Zxx = signal.stft(
            x,
            fs=self.sample_rate,
            nperseg=self.nfft,
            axis=-1
        )

        # WPE 사용 여부 선택
        # refined_doa_wpe_iterations: 0 이면 WPE OFF, MUSIC only
        if self.use_wpe:
            if wpe is None:
                raise RuntimeError(
                    "WPE is enabled, but nara_wpe is not available. "
                    "Install nara_wpe or set refined_doa_wpe_iterations: 0"
                )

            Zxx_for_doa = wpe(
                Zxx,
                taps=self.wpe_taps,
                delay=self.wpe_delay,
                iterations=self.wpe_iterations
            )
        else:
            Zxx_for_doa = Zxx

        self.doa_engine.locate_sources(Zxx_for_doa)

        math_angle = np.degrees(self.doa_engine.azimuth_recon[0])

        # 마이크 장착 방향/채널 기준 보정
        physical_angle = math_angle + self.hardware_offset_deg

        return self.wrap_deg_pm180(float(physical_angle))