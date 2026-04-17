import numpy as np
import pyroomacoustics as pra
from scipy import signal
from nara_wpe.wpe import wpe


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
        self.sample_rate = sample_rate
        self.nfft = nfft
        self.mic_channel_indices = tuple(mic_channel_indices)
        self.hardware_offset_deg = hardware_offset_deg
        self.wpe_taps = wpe_taps
        self.wpe_delay = wpe_delay
        self.wpe_iterations = wpe_iterations

        num_mics = len(self.mic_channel_indices)
        angles = np.linspace(0, 2 * np.pi, num_mics, endpoint=False)

        self.mic_locs = np.c_[
            mic_radius * np.cos(angles),
            mic_radius * np.sin(angles),
            np.zeros(num_mics)
        ].T

        self.doa_engine = pra.doa.algorithms['MUSIC'](
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
        audio_multich shape: (num_samples, num_input_channels)
        반환값: 하드웨어 기준 보정만 적용된 native angle (-180 ~ 180)
        최종 리매핑(front 기준, 부호 방향)은 외부에서 따로 수행한다.
        """
        if audio_multich.ndim != 2:
            raise ValueError(f"audio_multich must be 2-D, got shape={audio_multich.shape}")

        x = audio_multich[:, self.mic_channel_indices].astype(np.float32).T  # (M, N)

        if x.shape[1] < self.nfft:
            raise ValueError(f"not enough samples for STFT: {x.shape[1]} < {self.nfft}")

        _, _, Zxx = signal.stft(
            x,
            fs=self.sample_rate,
            nperseg=self.nfft,
            axis=-1
        )

        Zxx_clean = wpe(
            Zxx,
            taps=self.wpe_taps,
            delay=self.wpe_delay,
            iterations=self.wpe_iterations
        )

        self.doa_engine.locate_sources(Zxx_clean)

        math_angle = np.degrees(self.doa_engine.azimuth_recon[0])
        physical_angle = math_angle + self.hardware_offset_deg

        return self.wrap_deg_pm180(float(physical_angle))
